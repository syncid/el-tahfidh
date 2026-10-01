<?php

declare(strict_types=1);

namespace MyCustomApp\Models;

/**
 * Operasi data booking survei yang dibutuhkan Service.
 * Dipisah sebagai interface agar Service bisa diuji dengan repository palsu.
 */
interface SurveyBookingRepositoryInterface
{
    public const STATUS_TERJADWAL = 'terjadwal';
    public const STATUS_HADIR     = 'hadir';
    public const STATUS_BATAL     = 'batal';
    public const STATUSES         = [self::STATUS_TERJADWAL, self::STATUS_HADIR, self::STATUS_BATAL];

    /**
     * Booking yang belum dibatalkan untuk anak yang sama di tanggal yang sama.
     *
     * @return array<string, mixed>|null
     */
    public function find_active_duplicate(string $wa, string $santri, string $tanggal): ?array;

    /**
     * @param array<string, mixed> $data
     */
    public function insert(array $data): int;

    /**
     * @param array<string, mixed> $data
     */
    public function update(int $id, array $data): bool;
}
