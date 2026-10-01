<?php

declare(strict_types=1);

namespace MyCustomApp\Models;

use InvalidArgumentException;
use RuntimeException;
use wpdb;

/**
 * Basis Model untuk tabel kustom. Satu-satunya lapisan yang boleh menyentuh $wpdb.
 *
 * Keamanan:
 * - Nama kolom hanya dari whitelist columns(); key lain dibuang (cegah injeksi via nama kolom).
 * - Nilai selalu lewat placeholder $wpdb (prepare/insert/update/delete).
 * - Identifier tabel memakai placeholder %i (WordPress 6.2+).
 *
 * Contoh turunan:
 *   final class RegistrationRepository extends AbstractRepository {
 *       protected function table_suffix(): string { return 'mca_registrations'; }
 *       protected function columns(): array { return ['nama' => '%s', 'umur' => '%d']; }
 *   }
 */
abstract class AbstractRepository
{
    public function __construct(protected readonly wpdb $db)
    {
    }

    /**
     * Nama tabel tanpa prefix WordPress, mis. 'mca_registrations'.
     */
    abstract protected function table_suffix(): string;

    /**
     * Kolom yang boleh ditulis beserta format $wpdb ('%s', '%d', '%f').
     * Jangan masukkan 'id' (auto increment).
     *
     * @return array<string, string>
     */
    abstract protected function columns(): array;

    final public function table(): string
    {
        return $this->db->prefix . $this->table_suffix();
    }

    /**
     * @return array<string, mixed>|null
     */
    public function find(int $id): ?array
    {
        $row = $this->db->get_row(
            $this->db->prepare('SELECT * FROM %i WHERE id = %d', $this->table(), $id),
            ARRAY_A
        );

        return is_array($row) ? $row : null;
    }

    /**
     * @param array<string, mixed> $data
     * @return int ID baris baru.
     */
    public function insert(array $data): int
    {
        [$values, $formats] = $this->whitelist($data);

        if ($values === []) {
            throw new InvalidArgumentException('Tidak ada kolom valid untuk disimpan.');
        }

        if ($this->db->insert($this->table(), $values, $formats) === false) {
            throw new RuntimeException(sprintf('Insert ke %s gagal: %s', $this->table(), $this->db->last_error));
        }

        return (int) $this->db->insert_id;
    }

    /**
     * @param array<string, mixed> $data
     * @return bool true jika ada baris yang berubah.
     */
    public function update(int $id, array $data): bool
    {
        [$values, $formats] = $this->whitelist($data);

        if ($values === []) {
            return false;
        }

        $result = $this->db->update($this->table(), $values, ['id' => $id], $formats, ['%d']);

        if ($result === false) {
            throw new RuntimeException(sprintf('Update %s#%d gagal: %s', $this->table(), $id, $this->db->last_error));
        }

        return $result > 0;
    }

    /**
     * @return bool true jika baris terhapus.
     */
    public function delete(int $id): bool
    {
        $result = $this->db->delete($this->table(), ['id' => $id], ['%d']);

        if ($result === false) {
            throw new RuntimeException(sprintf('Delete %s#%d gagal: %s', $this->table(), $id, $this->db->last_error));
        }

        return $result > 0;
    }

    /**
     * Saring data ke kolom yang diizinkan; format disusun sesuai urutan data.
     *
     * @param array<string, mixed> $data
     * @return array{0: array<string, mixed>, 1: list<string>}
     */
    private function whitelist(array $data): array
    {
        $columns = $this->columns();
        $values  = [];
        $formats = [];

        foreach ($data as $column => $value) {
            if (isset($columns[$column])) {
                $values[$column] = $value;
                $formats[]       = $columns[$column];
            }
        }

        return [$values, $formats];
    }
}
