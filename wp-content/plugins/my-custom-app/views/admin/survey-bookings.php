<?php
/**
 * Template halaman admin Booking Survei.
 *
 * Variabel: $view = [items, total, page, per_page, filters, statuses, page_slug,
 *                    status_action, export_action, notice]
 * Semua output di-escape.
 *
 * @var array<string, mixed> $view
 */

declare(strict_types=1);

use MyCustomApp\Helpers\DateFormatter;

defined('ABSPATH') || exit;

$filters     = $view['filters'];
$total_pages = (int) ceil($view['total'] / max(1, $view['per_page']));
$labels      = [
    'terjadwal' => __('Terjadwal', 'my-custom-app'),
    'hadir'     => __('Hadir', 'my-custom-app'),
    'batal'     => __('Batal', 'my-custom-app'),
];
?>
<div class="wrap">
    <h1 class="wp-heading-inline"><?php esc_html_e('Booking Survei', 'my-custom-app'); ?></h1>
    <hr class="wp-header-end">

    <?php if ($view['notice'] === 'status') : ?>
        <div class="notice notice-success is-dismissible"><p><?php esc_html_e('Status booking diperbarui.', 'my-custom-app'); ?></p></div>
    <?php endif; ?>

    <form method="get" class="mca-filters" style="display:flex;flex-wrap:wrap;gap:8px;align-items:flex-end;margin:16px 0;">
        <input type="hidden" name="page" value="<?php echo esc_attr($view['page_slug']); ?>">
        <label><?php esc_html_e('Dari', 'my-custom-app'); ?><br>
            <input type="date" name="dari" value="<?php echo esc_attr($filters['dari']); ?>">
        </label>
        <label><?php esc_html_e('Sampai', 'my-custom-app'); ?><br>
            <input type="date" name="sampai" value="<?php echo esc_attr($filters['sampai']); ?>">
        </label>
        <label><?php esc_html_e('Status', 'my-custom-app'); ?><br>
            <select name="status">
                <option value=""><?php esc_html_e('Semua', 'my-custom-app'); ?></option>
                <?php foreach ($view['statuses'] as $status) : ?>
                    <option value="<?php echo esc_attr($status); ?>" <?php selected($filters['status'], $status); ?>><?php echo esc_html($labels[$status] ?? $status); ?></option>
                <?php endforeach; ?>
            </select>
        </label>
        <label><?php esc_html_e('Cari', 'my-custom-app'); ?><br>
            <input type="search" name="cari" value="<?php echo esc_attr($filters['cari']); ?>" placeholder="<?php esc_attr_e('Nama, kode, atau WA', 'my-custom-app'); ?>">
        </label>
        <?php submit_button(__('Terapkan', 'my-custom-app'), 'secondary', '', false); ?>
    </form>

    <form method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>" style="margin-bottom:12px;">
        <input type="hidden" name="action" value="<?php echo esc_attr($view['export_action']); ?>">
        <?php wp_nonce_field($view['export_action']); ?>
        <?php foreach (['dari', 'sampai', 'status', 'cari'] as $key) : ?>
            <input type="hidden" name="<?php echo esc_attr($key); ?>" value="<?php echo esc_attr($filters[$key]); ?>">
        <?php endforeach; ?>
        <?php submit_button(__('Ekspor CSV', 'my-custom-app'), 'secondary', '', false); ?>
        <span class="description" style="margin-left:8px;">
            <?php
            /* translators: %s: jumlah booking */
            echo esc_html(sprintf(_n('%s booking sesuai filter', '%s booking sesuai filter', (int) $view['total'], 'my-custom-app'), number_format_i18n((int) $view['total'])));
            ?>
        </span>
    </form>

    <table class="widefat striped">
        <thead>
            <tr>
                <th><?php esc_html_e('Kode', 'my-custom-app'); ?></th>
                <th><?php esc_html_e('Jadwal', 'my-custom-app'); ?></th>
                <th><?php esc_html_e('Calon santri', 'my-custom-app'); ?></th>
                <th><?php esc_html_e('Orang tua', 'my-custom-app'); ?></th>
                <th><?php esc_html_e('Domisili', 'my-custom-app'); ?></th>
                <th><?php esc_html_e('Dibuat', 'my-custom-app'); ?></th>
                <th><?php esc_html_e('Status', 'my-custom-app'); ?></th>
            </tr>
        </thead>
        <tbody>
        <?php if ($view['items'] === []) : ?>
            <tr><td colspan="7"><?php esc_html_e('Belum ada booking untuk filter ini.', 'my-custom-app'); ?></td></tr>
        <?php endif; ?>
        <?php foreach ($view['items'] as $row) : ?>
            <tr>
                <td><strong><?php echo esc_html((string) $row['kode']); ?></strong></td>
                <td>
                    <?php echo esc_html(DateFormatter::date((string) $row['tanggal'])); ?><br>
                    <span class="description"><?php echo esc_html((string) $row['sesi']); ?> WIB</span>
                </td>
                <td>
                    <?php echo esc_html((string) $row['santri']); ?><br>
                    <span class="description"><?php echo esc_html($row['jenjang'] . ', ' . $row['kelas']); ?></span>
                </td>
                <td>
                    <?php echo esc_html((string) $row['ortu']); ?><br>
                    <a href="<?php echo esc_url('https://wa.me/' . rawurlencode((string) $row['wa'])); ?>" target="_blank" rel="noopener noreferrer">+<?php echo esc_html((string) $row['wa']); ?></a>
                </td>
                <td><?php echo esc_html((string) $row['domisili']); ?></td>
                <td><?php echo esc_html(DateFormatter::utc_datetime((string) $row['created_at'])); ?></td>
                <td>
                    <form method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>" style="display:flex;gap:4px;">
                        <input type="hidden" name="action" value="<?php echo esc_attr($view['status_action']); ?>">
                        <input type="hidden" name="id" value="<?php echo esc_attr((string) $row['id']); ?>">
                        <?php wp_nonce_field($view['status_action'] . '_' . (int) $row['id']); ?>
                        <select name="status" aria-label="<?php esc_attr_e('Ubah status', 'my-custom-app'); ?>">
                            <?php foreach ($view['statuses'] as $status) : ?>
                                <option value="<?php echo esc_attr($status); ?>" <?php selected($row['status'], $status); ?>><?php echo esc_html($labels[$status] ?? $status); ?></option>
                            <?php endforeach; ?>
                        </select>
                        <?php submit_button(__('Simpan', 'my-custom-app'), 'small', '', false); ?>
                    </form>
                </td>
            </tr>
        <?php endforeach; ?>
        </tbody>
    </table>

    <?php if ($total_pages > 1) : ?>
        <div class="tablenav"><div class="tablenav-pages">
            <?php
            echo wp_kses_post(
                (string) paginate_links(
                    [
                        'base'    => add_query_arg('paged', '%#%'),
                        'format'  => '',
                        'current' => (int) $view['page'],
                        'total'   => $total_pages,
                    ]
                )
            );
            ?>
        </div></div>
    <?php endif; ?>
</div>
