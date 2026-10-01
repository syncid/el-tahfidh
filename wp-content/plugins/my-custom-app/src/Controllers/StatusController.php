<?php

declare(strict_types=1);

namespace MyCustomApp\Controllers;

use MyCustomApp\Helpers\ResponseFormatter;
use MyCustomApp\Services\StatusService;
use WP_Error;
use WP_REST_Request;
use WP_REST_Response;
use WP_REST_Server;

/**
 * GET /wp-json/my-custom-app/v1/status
 *
 * Endpoint diagnostik khusus administrator untuk memastikan rantai
 * Provider -> Controller -> Service berjalan.
 */
final class StatusController extends AbstractRestController
{
    public function __construct(private readonly StatusService $status)
    {
    }

    public function register_routes(): void
    {
        $this->route(
            '/status',
            WP_REST_Server::READABLE,
            [$this, 'show'],
            $this->require_capability('manage_options')
        );
    }

    public function show(WP_REST_Request $request): WP_REST_Response|WP_Error
    {
        return $this->handle(fn (): WP_REST_Response => ResponseFormatter::success($this->status->report()));
    }
}
