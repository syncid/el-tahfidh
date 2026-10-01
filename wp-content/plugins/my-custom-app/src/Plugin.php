<?php

declare(strict_types=1);

namespace MyCustomApp;

use MyCustomApp\Providers\HookableInterface;

/**
 * Kelas utama plugin: merakit dependensi lalu mengaktifkan semua provider.
 *
 * Constructor menerima provider lewat dependency injection (mudah diuji);
 * create() adalah composition root, satu-satunya tempat objek dirakit.
 */
final class Plugin
{
    /** @var list<HookableInterface> */
    private readonly array $providers;

    private bool $booted = false;

    public function __construct(
        private readonly string $plugin_file,
        HookableInterface ...$providers
    ) {
        $this->providers = array_values($providers);
    }

    /**
     * Composition root. Tambahkan provider baru di sini beserta dependensinya.
     */
    public static function create(string $plugin_file): self
    {
        $clock    = new Services\WpClock();
        $bookings = new Models\SurveyBookingRepository($GLOBALS['wpdb']);

        return new self(
            $plugin_file,
            new Providers\InstallProvider(new Services\Installer($bookings)),
            new Providers\RestProvider(
                new Controllers\StatusController(new Services\StatusService($plugin_file)),
                new Controllers\SurveyBookingController(
                    new Services\SurveyBookingService(
                        $bookings,
                        new Services\SurveyBookingValidator($clock),
                        new Services\RateLimiter(),
                        $clock
                    ),
                    ['https://eltahfidh.github.io']
                ),
            ),
            new Providers\AdminProvider(new Controllers\Admin\SurveyBookingAdminController($bookings, $clock)),
        );
    }

    /**
     * Daftarkan hook semua provider. Aman dipanggil berkali-kali.
     */
    public function boot(): void
    {
        if ($this->booted) {
            return;
        }

        foreach ($this->providers as $provider) {
            $provider->register_hooks();
        }

        $this->booted = true;
    }

    public function plugin_file(): string
    {
        return $this->plugin_file;
    }
}
