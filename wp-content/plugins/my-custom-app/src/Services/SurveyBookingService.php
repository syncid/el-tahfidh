<?php

declare(strict_types=1);

namespace MyCustomApp\Services;

use DateTimeZone;
use MyCustomApp\Models\SurveyBookingRepositoryInterface;

/**
 * Logika bisnis booking survei: anti-spam, validasi, cegah booking ganda, buat kode.
 */
final class SurveyBookingService
{
    /** Maksimal percobaan booking per IP dalam satu jendela waktu. */
    public const RATE_LIMIT = 10;
    public const RATE_WINDOW = 600; // detik

    private const PESAN_GAGAL = 'Booking belum tersimpan. Silakan coba lagi.';

    public function __construct(
        private readonly SurveyBookingRepositoryInterface $bookings,
        private readonly SurveyBookingValidator $validator,
        private readonly RateLimiter $limiter,
        private readonly ClockInterface $clock
    ) {
    }

    /**
     * @param array<string, mixed> $input     Data dari form (termasuk honeypot 'website').
     * @param string               $client_ip Identitas untuk rate limit.
     * @throws ValidationException Pesan aman ditampilkan ke pengguna.
     */
    public function book(array $input, string $client_ip): BookingResult
    {
        // Honeypot: field tersembunyi yang hanya diisi bot.
        $honeypot = $input['website'] ?? '';
        if (! is_string($honeypot) || trim($honeypot) !== '') {
            throw new ValidationException(self::PESAN_GAGAL, [], 400);
        }

        if (! $this->limiter->attempt('survey_booking', $client_ip, self::RATE_LIMIT, self::RATE_WINDOW)) {
            throw new ValidationException(
                'Terlalu banyak percobaan booking. Silakan coba lagi beberapa menit lagi.',
                [],
                429
            );
        }

        $data = $this->validator->validate($input);

        // Anak yang sama sudah terjadwal di tanggal ini: kembalikan tiket lama.
        $existing = $this->bookings->find_active_duplicate($data['wa'], $data['santri'], $data['tanggal']);
        if ($existing !== null && ! empty($existing['kode'])) {
            return new BookingResult((string) $existing['kode'], (string) $existing['sesi'], true);
        }

        $now = $this->clock->now();
        $id  = $this->bookings->insert(
            $data + [
                'status'     => SurveyBookingRepositoryInterface::STATUS_TERJADWAL,
                'created_at' => $now->setTimezone(new DateTimeZone('UTC'))->format('Y-m-d H:i:s'),
            ]
        );

        // Kode dari ID: unik tanpa risiko tabrakan, mis. SMP-26007.
        $kode = sprintf('%s-%s%03d', $data['jenjang'], $now->format('y'), $id);
        $this->bookings->update($id, ['kode' => $kode]);

        return new BookingResult($kode, $data['sesi'], false);
    }
}
