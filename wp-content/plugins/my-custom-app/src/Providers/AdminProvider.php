<?php

declare(strict_types=1);

namespace MyCustomApp\Providers;

use MyCustomApp\Controllers\Admin\SurveyBookingAdminController;

/**
 * Menu wp-admin dan handler admin-post.php (hanya user login; sengaja tanpa admin_post_nopriv_).
 */
final class AdminProvider implements HookableInterface
{
    public function __construct(private readonly SurveyBookingAdminController $bookings)
    {
    }

    public function register_hooks(): void
    {
        add_action('admin_menu', [$this->bookings, 'register_menu']);
        add_action('admin_post_' . SurveyBookingAdminController::ACTION_STATUS, [$this->bookings, 'handle_status']);
        add_action('admin_post_' . SurveyBookingAdminController::ACTION_EXPORT, [$this->bookings, 'handle_export']);
    }
}
