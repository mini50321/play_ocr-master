<?php
defined('_JEXEC') or die;

use Joomla\CMS\Factory;

$app = Factory::getApplication();
$input = $app->input;
$show_id = $input->getInt('id', $params->get('show_id', 0));

$api_base_url = $params->get('api_base_url', 'https://www.broadwayandmain.com/playbill_app/api/joomla');
$public_base_url = $params->get('public_base_url', 'https://www.broadwayandmain.com/playbill_app/public');
$profile_base_url = $params->get('profile_base_url', $public_base_url);
$module_enabled = $params->get('module_enabled', 1);

if (!$module_enabled || empty($show_id)) {
    return;
}

$show_data = ModPlaybillShowHelper::getShowData($show_id, $api_base_url, $public_base_url);

if (!$show_data) {
    if (Factory::getApplication()->get('debug')) {
        echo '<div class="playbill-error" style="padding: 10px; background: #fee; border: 1px solid #fcc; color: #c00; border-radius: 4px; margin: 10px 0;">';
        echo 'Playbill Show Module: Show not found or error loading data for Show ID ' . htmlspecialchars($show_id) . '.';
        echo '</div>';
    }
    return;
}

if (empty($show_data['productions'])) {
    echo '<div class="playbill-show-module" style="margin: 20px 0; padding: 20px; border: 1px solid #e5e7eb; border-radius: 8px; background: #fff;">';
    echo '<h2 class="playbill-title" style="font-size: 28px; font-weight: bold; margin-bottom: 15px; color: #1f2937;">';
    echo htmlspecialchars($show_data['title']);
    echo '</h2>';
    echo '<p style="color: #6b7280; padding: 20px; text-align: center;">No productions found for this show.</p>';
    echo '</div>';
    return;
}

$latest_production = $show_data['productions'][0];
$credits_by_category = ModPlaybillShowHelper::groupCreditsByCategory($latest_production['credits']);

?>
<div class="playbill-show-module" style="margin: 20px 0; padding: 20px; border: 1px solid #e5e7eb; border-radius: 8px; background: #fff;">
    <h2 class="playbill-title" style="font-size: 28px; font-weight: bold; margin-bottom: 15px; color: #1f2937;">
        <?php echo htmlspecialchars($show_data['title']); ?>
    </h2>
    
    <div style="margin-bottom: 20px; padding: 15px; background: #f9fafb; border-radius: 6px; border-left: 4px solid #4f46e5;">
        <p style="margin: 0; color: #6b7280; font-size: 16px;">
            <strong style="color: #1f2937;">Theater:</strong> 
            <?php echo htmlspecialchars($latest_production['theater']['name']); ?>
        </p>
        <p style="margin: 5px 0 0 0; color: #6b7280; font-size: 16px;">
            <strong style="color: #1f2937;">Year:</strong> 
            <?php echo (int)$latest_production['year']; ?>
        </p>
    </div>
    
    <?php if (!empty($credits_by_category)): ?>
    <?php foreach ($credits_by_category as $category => $credits): ?>
    <div class="playbill-category" style="margin-bottom: 30px;">
        <h3 style="font-size: 20px; font-weight: 600; margin-bottom: 15px; color: #4b5563; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 2px solid #e5e7eb; padding-bottom: 8px;">
            <?php echo htmlspecialchars($category); ?>
        </h3>
        <ul style="list-style: none; padding: 0; margin: 0;">
            <?php foreach ($credits as $credit): ?>
            <li style="padding: 10px 0; border-bottom: 1px solid #f3f4f6;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong style="font-size: 16px; color: #1f2937;">
                            <?php 
                            $person_url = '';
                            if (strpos($profile_base_url, 'index.php') !== false || strpos($profile_base_url, '?') !== false) {
                                $separator = (strpos($profile_base_url, '?') !== false) ? '&' : '?';
                                $person_url = $profile_base_url . $separator . 'id=' . $credit['person']['id'] . '&type=actor';
                            } else {
                                $person_url = $profile_base_url . '/actor/' . $credit['person']['id'];
                            }
                            ?>
                            <a href="<?php echo htmlspecialchars($person_url); ?>" style="color: #4f46e5; text-decoration: none;">
                                <?php echo htmlspecialchars($credit['person']['name']); ?>
                            </a>
                        </strong>
                        <?php if (!empty($credit['role']) && $credit['role'] !== $category): ?>
                            <span style="color: #6b7280; margin-left: 8px;">as <?php echo htmlspecialchars($credit['role']); ?></span>
                        <?php endif; ?>
                        <?php if ($credit['is_equity']): ?>
                            <span style="color: #10b981; font-weight: 600; margin-left: 5px;">*</span>
                        <?php endif; ?>
                    </div>
                </div>
            </li>
            <?php endforeach; ?>
        </ul>
    </div>
    <?php endforeach; ?>
    <?php else: ?>
    <p style="color: #6b7280; padding: 20px; text-align: center;">No credits found for this production.</p>
    <?php endif; ?>
</div>

