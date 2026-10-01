<?php

declare(strict_types=1);

namespace MyCustomApp\Providers;

use MyCustomApp\Controllers\RestControllerInterface;

/**
 * Mendaftarkan semua controller REST ke WordPress pada rest_api_init.
 */
final class RestProvider implements HookableInterface
{
    /** @var list<RestControllerInterface> */
    private readonly array $controllers;

    public function __construct(RestControllerInterface ...$controllers)
    {
        $this->controllers = array_values($controllers);
    }

    public function register_hooks(): void
    {
        add_action('rest_api_init', [$this, 'register_routes']);
    }

    /**
     * Callback rest_api_init. Jangan dipanggil langsung.
     */
    public function register_routes(): void
    {
        foreach ($this->controllers as $controller) {
            $controller->register_routes();
        }
    }
}
