<?php

declare(strict_types=1);

namespace MyCustomApp\Models;

use InvalidArgumentException;

/**
 * Tabel {prefix}mca_survey_bookings: booking kunjungan/survei calon santri.
 */
final class SurveyBookingRepository extends AbstractRepository implements SchemaInterface, SurveyBookingRepositoryInterface
{
    protected function table_suffix(): string
    {
        return 'mca_survey_bookings';
    }

    protected function columns(): array
    {
        return [
            'kode'       => '%s',
            'jenjang'    => '%s',
            'ortu'       => '%s',
            'wa'         => '%s',
            'santri'     => '%s',
            'kelas'      => '%s',
            'domisili'   => '%s',
            'tanggal'    => '%s',
            'sesi'       => '%s',
            'status'     => '%s',
            'created_at' => '%s',
        ];
    }

    public function schema_sql(): string
    {
        $table   = $this->table();
        $charset = $this->db->get_charset_collate();

        return "CREATE TABLE {$table} (
  id bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  kode varchar(20) DEFAULT NULL,
  jenjang varchar(3) NOT NULL,
  ortu varchar(100) NOT NULL,
  wa varchar(20) NOT NULL,
  santri varchar(100) NOT NULL,
  kelas varchar(30) NOT NULL,
  domisili varchar(100) NOT NULL,
  tanggal date NOT NULL,
  sesi char(5) NOT NULL,
  status varchar(20) NOT NULL DEFAULT 'terjadwal',
  created_at datetime NOT NULL,
  PRIMARY KEY  (id),
  UNIQUE KEY kode (kode),
  KEY tanggal_sesi (tanggal,sesi),
  KEY wa_tanggal (wa,tanggal)
) {$charset};";
    }

    public function find_active_duplicate(string $wa, string $santri, string $tanggal): ?array
    {
        $row = $this->db->get_row(
            $this->db->prepare(
                'SELECT * FROM %i WHERE wa = %s AND santri = %s AND tanggal = %s AND status <> %s ORDER BY id ASC LIMIT 1',
                $this->table(),
                $wa,
                $santri,
                $tanggal,
                self::STATUS_BATAL
            ),
            ARRAY_A
        );

        return is_array($row) ? $row : null;
    }

    /**
     * @param array{dari?: string, sampai?: string, status?: string, cari?: string} $filters
     * @return array{items: list<array<string, mixed>>, total: int}
     */
    public function paginate(array $filters, int $page, int $per_page): array
    {
        [$where, $params] = $this->where($filters);

        $total = (int) $this->db->get_var(
            $this->db->prepare("SELECT COUNT(*) FROM %i WHERE {$where}", $this->table(), ...$params)
        );

        $args  = [$this->table(), ...$params, $per_page, max(0, ($page - 1) * $per_page)];
        $items = $this->db->get_results(
            $this->db->prepare(
                "SELECT * FROM %i WHERE {$where} ORDER BY tanggal ASC, sesi ASC, id ASC LIMIT %d OFFSET %d",
                ...$args
            ),
            ARRAY_A
        );

        return ['items' => is_array($items) ? $items : [], 'total' => $total];
    }

    /**
     * Semua baris sesuai filter (untuk ekspor CSV).
     *
     * @param array{dari?: string, sampai?: string, status?: string, cari?: string} $filters
     * @return list<array<string, mixed>>
     */
    public function all(array $filters): array
    {
        [$where, $params] = $this->where($filters);

        $rows = $this->db->get_results(
            $this->db->prepare(
                "SELECT * FROM %i WHERE {$where} ORDER BY tanggal ASC, sesi ASC, id ASC",
                $this->table(),
                ...$params
            ),
            ARRAY_A
        );

        return is_array($rows) ? $rows : [];
    }

    public function set_status(int $id, string $status): bool
    {
        if (! in_array($status, self::STATUSES, true)) {
            throw new InvalidArgumentException(sprintf('Status tidak dikenal: %s', $status));
        }

        return $this->update($id, ['status' => $status]);
    }

    /**
     * Susun klausa WHERE dari potongan SQL tetap + placeholder. Nilai filter
     * TIDAK pernah disisipkan langsung; semuanya lewat $params untuk prepare().
     *
     * @param array{dari?: string, sampai?: string, status?: string, cari?: string} $filters
     * @return array{0: string, 1: list<string>}
     */
    private function where(array $filters): array
    {
        $clauses = ['1=1'];
        $params  = [];

        if (! empty($filters['dari'])) {
            $clauses[] = 'tanggal >= %s';
            $params[]  = $filters['dari'];
        }

        if (! empty($filters['sampai'])) {
            $clauses[] = 'tanggal <= %s';
            $params[]  = $filters['sampai'];
        }

        if (! empty($filters['status']) && in_array($filters['status'], self::STATUSES, true)) {
            $clauses[] = 'status = %s';
            $params[]  = $filters['status'];
        }

        if (! empty($filters['cari'])) {
            $like      = '%' . $this->db->esc_like($filters['cari']) . '%';
            $clauses[] = '(santri LIKE %s OR ortu LIKE %s OR kode LIKE %s OR wa LIKE %s)';
            array_push($params, $like, $like, $like, $like);
        }

        return [implode(' AND ', $clauses), $params];
    }
}
