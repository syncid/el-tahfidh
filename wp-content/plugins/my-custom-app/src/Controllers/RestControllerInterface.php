<?php

declare(strict_types=1);

namespace MyCustomApp\Controllers;

/**
 * Kontrak controller REST. Dipanggil oleh RestProvider saat rest_api_init.
 */
interface RestControllerInterface
{
    /**
     * Daftarkan semua route milik controller ini (register_rest_route).
     */
    public function register_routes(): void;
}
