<?php

declare(strict_types=1);

namespace MyCustomApp\Controllers\Admin;

use MyCustomApp\Helpers\Capabilities;
use MyCustomApp\Helpers\Sanitizer;
use MyCustomApp\Helpers\Security;
use MyCustomApp\Helpers\View;
use MyCustomApp\Models\SurveyBookingRepository;
use MyCustomApp\Models\SurveyBookingRepositoryInterface;
use MyCustomApp\Services\ClockInterface;

/**
 * Halaman wp-admin "Booking Survei": daftar + filter, ubah status, ekspor CSV.
 *
 * Semua aksi tulis lewat admin-post.php (khusus user login) dan WAJIB lolos
 * nonce + current_user_can(Capabilities::MANAGE_BOOKINGS).
 */
final class SurveyBookingAdminController
{
    public const PAGE_SLUG     = 'mca-survey-bookings';
    public const ACTION_STATUS = 'mca_booking_status';
    public const ACTION_EXPORT = 'mca_booking_export';

    private const PER_PAGE = 30;

    public function __construct(
        private readonly SurveyBookingRepository $bookings,
        private readonly ClockInterface $clock
    ) {
    }

    /**
     * Callback admin_menu.
     */
    public function register_menu(): void
    {
        add_menu_page(
            __('Booking Survei', 'my-custom-app'),
            __('Booking Survei', 'my-custom-app'),
            Capabilities::MANAGE_BOOKINGS,
            self::PAGE_SLUG,
            [$this, 'render'],
            'dashicons-calendar-alt',
            26
        );
    }

    /**
     * Render daftar booking. Request GET baca-saja, jadi tidak perlu nonce.
     */
    public function render(): void
    {
        Security::require_capability_or_die(Capabilities::MANAGE_BOOKINGS);

        // phpcs:ignore WordPress.Security.NonceVerification.Recommended -- filter tampilan, tidak mengubah data.
        $filters = $this->filters($_GET, true);
        // phpcs:ignore WordPress.Security.NonceVerification.Recommended
        $page   = max(1, (int) Sanitizer::value(is_string($_GET['paged'] ?? null) ? wp_unslash($_GET['paged']) : '1', 'int'));
        $result = $this->bookings->paginate($filters, $page, self::PER_PAGE);

        View::render(
            'admin/survey-bookings',
            [
                'items'         => $result['items'],
                'total'         => $result['total'],
                'page'          => $page,
                'per_page'      => self::PER_PAGE,
                'filters'       => $filters,
                'statuses'      => SurveyBookingRepositoryInterface::STATUSES,
                'page_slug'     => self::PAGE_SLUG,
                'status_action' => self::ACTION_STATUS,
                'export_action' => self::ACTION_EXPORT,
                // phpcs:ignore WordPress.Security.NonceVerification.Recommended
                'notice'        => (string) Sanitizer::by_schema($_GET, ['mca_notice' => 'key'])['mca_notice'],
            ]
        );
    }

    /**
     * Callback admin_post_{ACTION_STATUS}: ubah status satu booking.
     */
    public function handle_status(): void
    {
        $input = Sanitizer::by_schema($_POST, ['id' => 'int', 'status' => 'key']);
        $id    = (int) ($input['id'] ?? 0);

        // Nonce per baris: token untuk booking A tidak bisa dipakai untuk booking B.
        Security::verify_nonce_or_die(self::ACTION_STATUS . '_' . $id);
        Security::require_capability_or_die(Capabilities::MANAGE_BOOKINGS);

        if ($id <= 0 || ! in_array($input['status'], SurveyBookingRepositoryInterface::STATUSES, true)) {
            wp_die(esc_html__('Data tidak valid.', 'my-custom-app'), '', ['response' => 400]);
        }

        $this->bookings->set_status($id, (string) $input['status']);

        $back = wp_get_referer() ?: admin_url('admin.php?page=' . self::PAGE_SLUG);
        wp_safe_redirect(add_query_arg('mca_notice', 'status', $back));
        exit;
    }

    /**
     * Callback admin_post_{ACTION_EXPORT}: unduh CSV sesuai filter aktif.
     */
    public function handle_export(): void
    {
        Security::verify_nonce_or_die(self::ACTION_EXPORT);
        Security::require_capability_or_die(Capabilities::MANAGE_BOOKINGS);

        $rows     = $this->bookings->all($this->filters($_POST, false));
        $filename = 'booking-survei-' . $this->clock->now()->format('Ymd-His') . '.csv';

        nocache_headers();
        header('Content-Type: text/csv; charset=utf-8');
        header('Content-Disposition: attachment; filename="' . $filename . '"');
        header('X-Content-Type-Options: nosniff');

        $out = fopen('php://output', 'w');
        fwrite($out, "\xEF\xBB\xBF"); // BOM agar Excel membaca UTF-8.
        fputcsv($out, ['Kode', 'Tanggal', 'Sesi', 'Status', 'Calon santri', 'Jenjang', 'Kelas', 'Orang tua', 'WhatsApp', 'Domisili', 'Dibuat (UTC)']);

        foreach ($rows as $row) {
            fputcsv(
                $out,
                array_map(
                    [self::class, 'csv_cell'],
                    [
                        $row['kode'], $row['tanggal'], $row['sesi'], $row['status'], $row['santri'], $row['jenjang'],
                        $row['kelas'], $row['ortu'], $row['wa'], $row['domisili'], $row['created_at'],
                    ]
                )
            );
        }

        fclose($out);
        exit;
    }

    /**
     * Cegah CSV/formula injection: sel yang diawali = + - @ (atau tab/CR) diberi awalan '.
     */
    public static function csv_cell(mixed $value): string
    {
        $value = (string) $value;

        return preg_match('/^[=+\-@\t\r]/', $value) === 1 ? "'" . $value : $value;
    }

    /**
     * @param array<string, mixed> $source         $_GET atau $_POST.
     * @param bool                 $default_today  Tampilan awal hanya booking mulai hari ini.
     * @return array{dari: string, sampai: string, status: string, cari: string}
     */
    private function filters(array $source, bool $default_today): array
    {
        $f = Sanitizer::by_schema($source, ['dari' => 'text', 'sampai' => 'text', 'status' => 'key', 'cari' => 'text']);

        $filters = [
            'dari'   => self::ymd_or_empty((string) $f['dari']),
            'sampai' => self::ymd_or_empty((string) $f['sampai']),
            'status' => in_array($f['status'], SurveyBookingRepositoryInterface::STATUSES, true) ? (string) $f['status'] : '',
            'cari'   => mb_substr((string) $f['cari'], 0, 100),
        ];

        // Parameter 'dari' tidak ada sama sekali = kunjungan pertama ke halaman.
        if ($default_today && ! array_key_exists('dari', $source)) {
            $filters['dari'] = $this->clock->now()->format('Y-m-d');
        }

        return $filters;
    }

    private static function ymd_or_empty(string $value): string
    {
        return preg_match('/^\d{4}-\d{2}-\d{2}$/', $value) === 1 ? $value : '';
    }
}
