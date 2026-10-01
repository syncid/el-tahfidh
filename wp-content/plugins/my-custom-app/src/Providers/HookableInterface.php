<?php

declare(strict_types=1);

namespace MyCustomApp\Providers;

/**
 * Kontrak untuk setiap kelas yang perlu mendaftarkan hook ke WordPress Core.
 *
 * Semua add_action() / add_filter() milik sebuah kelas WAJIB diletakkan di
 * register_hooks(), bukan di constructor. Dengan begitu pembuatan objek bebas
 * efek samping (mudah diuji), dan Plugin::boot() menjadi satu-satunya titik
 * yang mengaktifkan hook.
 */
interface HookableInterface
{
    /**
     * Daftarkan action dan filter milik kelas ini.
     *
     * Dipanggil tepat satu kali oleh Plugin::boot(). Jangan menjalankan logika
     * bisnis, query database, atau output apa pun di sini.
     */
    public function register_hooks(): void;
}
