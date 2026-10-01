<?php

declare(strict_types=1);

namespace MyCustomApp\Helpers;

use WP_Error;
use WP_REST_Response;

/**
 * Format respons REST yang seragam.
 *
 * Sukses: { "success": true, "data": ... }
 * Error : format bawaan WP_Error di REST, { "code", "message", "data": { "status", "details" } }
 */
final class ResponseFormatter
{
    private function __construct()
    {
    }

    public static function success(mixed $data = null, int $status = 200): WP_REST_Response
    {
        return new WP_REST_Response(['success' => true, 'data' => $data], $status);
    }

    /**
     * @param array<string, mixed> $details Info tambahan yang AMAN ditampilkan ke klien
     *                                      (mis. daftar field yang tidak valid).
     */
    public static function error(string $code, string $message, int $status = 400, array $details = []): WP_Error
    {
        return new WP_Error($code, $message, ['status' => $status, 'details' => $details]);
    }
}
