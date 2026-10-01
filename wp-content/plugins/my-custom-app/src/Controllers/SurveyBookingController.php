<?php

declare(strict_types=1);

namespace MyCustomApp\Controllers;

use MyCustomApp\Helpers\ResponseFormatter;
use MyCustomApp\Services\SurveyBookingService;
use MyCustomApp\Services\ValidationException;
use Throwable;
use WP_Error;
use WP_REST_Request;
use WP_REST_Response;
use WP_REST_Server;

/**
 * POST /wp-json/my-custom-app/v1/survei/booking
 *
 * Pengganti Web App Google Apps Script untuk form eltahfidh.github.io/survei.
 * Kontraknya SAMA PERSIS dengan yang dipakai form, jadi form cukup mengganti CONFIG.API_URL:
 *   Request : body JSON {"action":"booking","data":{...}} (Content-Type text/plain diterima)
 *   Respons : {"ok":true,"kode":"SMP-26007"} | {"ok":true,"kode":"...","dobel":true,"sesi":"08.00"}
 *             | {"ok":false,"error":"pesan untuk pengguna"}
 *
 * PENGECUALIAN TERDOKUMENTASI dari aturan "wajib current_user_can() + nonce":
 * endpoint ini dipakai tamu tanpa login dari domain lain, jadi tidak ada user dan tidak
 * ada sesi yang bisa dibajak (CSRF tidak relevan). Penggantinya: allowlist Origin,
 * honeypot, rate limit per IP, batas ukuran body, dan validasi ketat di Service.
 */
final class SurveyBookingController extends AbstractRestController
{
    private const MAX_BODY_BYTES = 8192;

    /**
     * @param list<string> $allowed_origins Origin luar yang boleh mengirim booking,
     *                                      mis. 'https://eltahfidh.github.io'. Origin situs ini selalu diizinkan.
     */
    public function __construct(
        private readonly SurveyBookingService $service,
        private readonly array $allowed_origins
    ) {
    }

    public function register_routes(): void
    {
        $this->route('/survei/booking', WP_REST_Server::CREATABLE, [$this, 'store'], [$this, 'check_origin']);
    }

    /**
     * Permission callback. Bisa diperluas dengan filter 'my_custom_app_booking_origins'.
     */
    public function check_origin(WP_REST_Request $request): bool|WP_Error
    {
        $origin  = untrailingslashit((string) $request->get_header('origin'));
        $allowed = (array) apply_filters(
            'my_custom_app_booking_origins',
            [...$this->allowed_origins, self::site_origin()]
        );

        if ($origin !== '' && in_array($origin, $allowed, true)) {
            return true;
        }

        return ResponseFormatter::error(
            'mca_origin_forbidden',
            __('Asal permintaan tidak diizinkan.', 'my-custom-app'),
            403
        );
    }

    public function store(WP_REST_Request $request): WP_REST_Response
    {
        $body = $request->get_body();

        if (strlen($body) > self::MAX_BODY_BYTES) {
            return $this->reply(['ok' => false, 'error' => __('Data terlalu besar.', 'my-custom-app')], 413);
        }

        $payload = json_decode($body, true);

        if (! is_array($payload) || ($payload['action'] ?? null) !== 'booking' || ! is_array($payload['data'] ?? null)) {
            return $this->reply(['ok' => false, 'error' => __('Format permintaan tidak valid.', 'my-custom-app')], 400);
        }

        try {
            $result = $this->service->book($payload['data'], self::client_ip());
        } catch (ValidationException $e) {
            return $this->reply(
                ['ok' => false, 'error' => $e->getMessage(), 'fields' => $e->errors()],
                $e->http_status()
            );
        } catch (Throwable $e) {
            $this->log_exception($e);

            return $this->reply(
                ['ok' => false, 'error' => __('Booking belum tersimpan. Silakan coba lagi.', 'my-custom-app')],
                500
            );
        }

        $out = ['ok' => true, 'kode' => $result->kode];

        if ($result->dobel) {
            $out['dobel'] = true;
            $out['sesi']  = $result->sesi;
        }

        return $this->reply($out, $result->dobel ? 200 : 201);
    }

    /**
     * @param array<string, mixed> $body
     */
    private function reply(array $body, int $status): WP_REST_Response
    {
        $response = new WP_REST_Response($body, $status);
        $response->header('Cache-Control', 'no-store');

        return $response;
    }

    private static function site_origin(): string
    {
        $parts = wp_parse_url(home_url());

        if (! is_array($parts) || empty($parts['scheme']) || empty($parts['host'])) {
            return '';
        }

        return $parts['scheme'] . '://' . $parts['host'] . (isset($parts['port']) ? ':' . $parts['port'] : '');
    }

    /**
     * IP klien dari REMOTE_ADDR. Header X-Forwarded-For sengaja tidak dipercaya
     * karena mudah dipalsukan (lihat catatan Cloudflare di README).
     */
    private static function client_ip(): string
    {
        $ip = isset($_SERVER['REMOTE_ADDR']) ? sanitize_text_field(wp_unslash((string) $_SERVER['REMOTE_ADDR'])) : '';

        return filter_var($ip, FILTER_VALIDATE_IP) !== false ? $ip : 'unknown';
    }
}
