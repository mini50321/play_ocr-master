<?php
defined('_JEXEC') or die;

use Joomla\CMS\Factory;

$app = Factory::getApplication();
$input = $app->input;
$actor_id = $input->getInt('id', $params->get('actor_id', 0));

$api_base_url = $params->get('api_base_url', 'https://www.broadwayandmain.com/playbill_app/api/joomla');
$public_base_url = $params->get('public_base_url', 'https://www.broadwayandmain.com/playbill_app/public');
$module_enabled = $params->get('module_enabled', 1);

if (!$module_enabled || empty($actor_id)) {
    return;
}

$actor_data = ModPlaybillActorHelper::getActorData($actor_id, $api_base_url, $public_base_url);

if (!$actor_data) {
    if (Factory::getApplication()->get('debug')) {
        echo '<div class="playbill-error" style="padding: 10px; background: #fee; border: 1px solid #fcc; color: #c00; border-radius: 4px; margin: 10px 0;">';
        echo 'Playbill Actor Module: Actor not found or error loading data for Actor ID ' . htmlspecialchars($actor_id) . '.';
        echo '</div>';
    }
    return;
}

$credits_by_category = ModPlaybillActorHelper::groupCreditsByCategory($actor_data['credits']);

?>
<div class="playbill-actor-module" style="margin: 20px 0; padding: 20px; border: 1px solid #e5e7eb; border-radius: 8px; background: #fff;">
    <h2 class="playbill-title" style="font-size: 28px; font-weight: bold; margin-bottom: 15px; color: #1f2937;">
        <?php echo htmlspecialchars($actor_data['name']); ?>
    </h2>
    
    <?php if (!empty($actor_data['credits'])): ?>
    <p style="color: #6b7280; margin-bottom: 20px; font-size: 16px;">
        <?php echo count($actor_data['credits']); ?> credit(s)
    </p>
    
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
                            <a href="<?php echo htmlspecialchars($public_base_url . '/show/' . $credit['show']['id']); ?>" style="color: #4f46e5; text-decoration: none;">
                                <?php echo htmlspecialchars($credit['show']['title']); ?>
                            </a>
                        </strong>
                        <?php if (!empty($credit['role']) && $credit['role'] !== $category): ?>
                            <span style="color: #6b7280; margin-left: 8px;">as <?php echo htmlspecialchars($credit['role']); ?></span>
                        <?php endif; ?>
                        <?php if ($credit['is_equity']): ?>
                            <span style="color: #10b981; font-weight: 600; margin-left: 5px;">*</span>
                        <?php endif; ?>
                    </div>
                    <div style="color: #6b7280; font-size: 14px;">
                        <?php echo htmlspecialchars($credit['theater']['name']); ?> (<?php echo (int)$credit['year']; ?>)
                    </div>
                </div>
            </li>
            <?php endforeach; ?>
        </ul>
    </div>
    <?php endforeach; ?>
    <?php else: ?>
    <p style="color: #6b7280; padding: 20px; text-align: center;">No credits found for this actor.</p>
    <?php endif; ?>
</div>

