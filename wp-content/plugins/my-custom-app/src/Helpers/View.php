<?php

declare(strict_types=1);

namespace MyCustomApp\Helpers;

use InvalidArgumentException;
use RuntimeException;

/**
 * Render template dari folder /views. Template menerima satu variabel: $view (array).
 * Setiap output di template WAJIB di-escape (esc_html, esc_attr, esc_url, wp_kses_post).
 */
final class View
{
    private function __construct()
    {
    }

    /**
     * @param string               $name Nama relatif tanpa .php, mis. 'admin/survey-bookings'.
     * @param array<string, mixed> $data
     */
    public static function render(string $name, array $data = []): void
    {
        // Hanya huruf kecil, angka, '-', '/': mencegah path traversal.
        if (preg_match('#^[a-z0-9\-]+(/[a-z0-9\-]+)*$#', $name) !== 1) {
            throw new InvalidArgumentException(sprintf('Nama view tidak valid: %s', $name));
        }

        $file = dirname(__DIR__, 2) . '/views/' . $name . '.php';

        if (! is_readable($file)) {
            throw new RuntimeException(sprintf('View tidak ditemukan: %s', $name));
        }

        // Scope terisolasi: template hanya melihat $view.
        (static function (string $__file, array $view): void {
            include $__file;
        })($file, $data);
    }
}
