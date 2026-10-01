<?php

declare(strict_types=1);

namespace MyCustomApp\Services;

use DateTimeImmutable;
use MyCustomApp\Helpers\Sanitizer;

/**
 * Validasi & normalisasi data booking survei.
 *
 * Aturannya sama dengan form di eltahfidh.github.io/survei, tetapi server
 * adalah otoritas akhir: data dari klien tidak pernah dipercaya.
 */
final class SurveyBookingValidator
{
    public const JENJANG   = ['SMP', 'SMA'];
    public const KELAS     = ['SD Kelas 5', 'SD Kelas 6', 'SMP Kelas 7', 'SMP Kelas 8', 'SMP Kelas 9', 'Lainnya'];
    public const SESI      = ['08.00', '11.00', '15.00'];
    public const MAKS_HARI = 60;

    private const MIN_TEKS = 2;
    private const MAKS_TEKS = 100;

    public function __construct(private readonly ClockInterface $clock)
    {
    }

    /**
     * @param array<string, mixed> $input Data mentah dari klien (JSON, tidak di-slash).
     * @return array{jenjang: string, ortu: string, wa: string, santri: string, kelas: string,
     *               domisili: string, tanggal: string, sesi: string}
     * @throws ValidationException
     */
    public function validate(array $input): array
    {
        $s = Sanitizer::by_schema(
            $input,
            [
                'jenjang'  => 'text',
                'ortu'     => 'text',
                'wa'       => 'text',
                'santri'   => 'text',
                'kelas'    => 'text',
                'domisili' => 'text',
                'tanggal'  => 'text',
                'sesi'     => 'text',
            ],
            false
        );

        $data = [
            'jenjang'  => strtoupper((string) $s['jenjang']),
            'ortu'     => self::capitalize((string) $s['ortu']),
            'wa'       => self::normalize_wa((string) $s['wa']),
            'santri'   => self::capitalize((string) $s['santri']),
            'kelas'    => (string) $s['kelas'],
            'domisili' => (string) $s['domisili'],
            'tanggal'  => (string) $s['tanggal'],
            'sesi'     => (string) $s['sesi'],
        ];

        $errors = [];

        if (! in_array($data['jenjang'], self::JENJANG, true)) {
            $errors['jenjang'] = 'Pilih SMP atau SMA.';
        }
        if (! self::length_ok($data['ortu'])) {
            $errors['ortu'] = 'Isi nama orang tua.';
        }
        if ($data['wa'] === '') {
            $errors['wa'] = 'Nomor WhatsApp belum benar. Contoh: 0812 3456 7890.';
        }
        if (! self::length_ok($data['santri'])) {
            $errors['santri'] = 'Isi nama calon santri.';
        }
        if (! in_array($data['kelas'], self::KELAS, true)) {
            $errors['kelas'] = 'Pilih kelas anak saat ini.';
        }
        if (! self::length_ok($data['domisili'])) {
            $errors['domisili'] = 'Isi kota atau kecamatan.';
        }

        $date_error = $this->date_error($data['tanggal']);
        if ($date_error !== null) {
            $errors['tanggal'] = $date_error;
        } elseif (! in_array($data['sesi'], self::SESI, true)) {
            $errors['sesi'] = 'Pilih sesi kedatangan.';
        } elseif (! $this->session_available($data['tanggal'], $data['sesi'])) {
            $errors['sesi'] = 'Sesi ini sudah lewat untuk hari ini. Pilih sesi atau tanggal lain.';
        }

        if ($errors !== []) {
            throw new ValidationException((string) reset($errors), $errors);
        }

        return $data;
    }

    /**
     * "ahmad  fauzi" -> "Ahmad Fauzi" (sama dengan fungsi kapital() di form).
     */
    public static function capitalize(string $value): string
    {
        $value = mb_strtolower(trim((string) preg_replace('/\s+/u', ' ', $value)), 'UTF-8');

        return (string) preg_replace_callback(
            '/(^|[\s\-.(])(\p{L})/u',
            static fn (array $m): string => $m[1] . mb_strtoupper($m[2], 'UTF-8'),
            $value
        );
    }

    /**
     * Normalisasi nomor WA ke format 628xxxxxxxxx. String kosong jika tidak valid.
     */
    public static function normalize_wa(string $value): string
    {
        $digits = (string) preg_replace('/\D/', '', $value);

        if (str_starts_with($digits, '0')) {
            $digits = '62' . substr($digits, 1);
        } elseif (str_starts_with($digits, '8')) {
            $digits = '62' . $digits;
        }

        return preg_match('/^628\d{7,12}$/', $digits) === 1 ? $digits : '';
    }

    private static function length_ok(string $value): bool
    {
        $length = mb_strlen($value, 'UTF-8');

        return $length >= self::MIN_TEKS && $length <= self::MAKS_TEKS;
    }

    private function date_error(string $tanggal): ?string
    {
        $tz   = $this->clock->now()->getTimezone();
        $date = DateTimeImmutable::createFromFormat('!Y-m-d', $tanggal, $tz);

        if ($date === false || $date->format('Y-m-d') !== $tanggal) {
            return 'Pilih tanggal survei.';
        }

        $today = $this->clock->now()->setTime(0, 0);

        if ($date < $today) {
            return 'Tanggal survei sudah lewat. Pilih tanggal lain.';
        }
        if ($date > $today->modify('+' . self::MAKS_HARI . ' days')) {
            return sprintf('Booking hanya bisa untuk %d hari ke depan.', self::MAKS_HARI);
        }

        return null;
    }

    /**
     * Untuk hari ini, sesi hanya bisa dipilih sebelum jamnya tiba.
     */
    private function session_available(string $tanggal, string $sesi): bool
    {
        $now = $this->clock->now();

        if ($tanggal !== $now->format('Y-m-d')) {
            return true;
        }

        return (int) $now->format('G') < (int) substr($sesi, 0, 2);
    }
}
