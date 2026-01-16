<?php
defined('_JEXEC') or die;

$show_id = $params->get('show_id', '');
$api_base_url = $params->get('api_base_url', 'https://www.broadwayandmain.com/playbill_app/api/joomla');
$public_base_url = $params->get('public_base_url', 'https://www.broadwayandmain.com/playbill_app/public');
$profile_base_url = $params->get('profile_base_url', '');
$module_enabled = $params->get('module_enabled', 1);

if (empty($profile_base_url)) {
    $profile_base_url = $public_base_url;
}

if (!$module_enabled || empty($show_id)) {
    return;
}

$production_data = ModPlaybillShowHelper::getProductionData($show_id, $api_base_url, $public_base_url);

if (!$production_data) {
    if (Factory::getApplication()->get('debug')) {
        echo '<div class="playbill-error" style="padding: 10px; background: #fee; border: 1px solid #fcc; color: #c00; border-radius: 4px; margin: 10px 0;">';
        echo 'Playbill Show Module: Show not found or error loading data for Show ID ' . htmlspecialchars($show_id) . '.';
        echo '</div>';
    }
    return;
}

$credits_by_category = ModPlaybillShowHelper::groupCreditsByCategory($production_data['credits']);

$cast_categories = ['Cast', 'Ensemble', 'Swings', 'Understudies'];
$crew_categories = ['Crew', 'Musician', 'Dance Captain'];
$creative_categories = ['Creative'];

$cast_credits = [];
$crew_credits = [];
$creative_credits = [];

foreach ($credits_by_category as $category => $credits) {
    $category_upper = strtoupper($category);
    if (in_array($category, $cast_categories) || in_array($category_upper, array_map('strtoupper', $cast_categories))) {
        $cast_credits = array_merge($cast_credits, $credits);
    } elseif (in_array($category, $crew_categories) || in_array($category_upper, array_map('strtoupper', $crew_categories))) {
        $crew_credits = array_merge($crew_credits, $credits);
    } elseif (in_array($category, $creative_categories) || in_array($category_upper, array_map('strtoupper', $creative_categories))) {
        $creative_credits = array_merge($creative_credits, $credits);
    } else {
        $cast_credits = array_merge($cast_credits, $credits);
    }
}

?>
<div class="playbill-show-module" style="margin: 20px 0; padding: 20px; border: 1px solid #e5e7eb; border-radius: 8px; background: #fff;">
    <h3 class="playbill-title" style="font-size: 24px; font-weight: bold; margin-bottom: 10px; color: #1f2937;">
        <?php echo htmlspecialchars($production_data['show']['title']); ?>
    </h3>
    <p class="playbill-theater" style="font-size: 16px; color: #6b7280; margin-bottom: 20px;">
        <?php echo htmlspecialchars($production_data['theater']['name']); ?>
        <?php if (isset($production_data['year']) && $production_data['year']): ?>
            (<?php echo (int)$production_data['year']; ?>)
        <?php endif; ?>
    </p>
    
    <?php if (!empty($cast_credits)): ?>
    <div class="playbill-cast" style="margin-bottom: 30px;">
        <h4 style="font-size: 18px; font-weight: 600; margin-bottom: 15px; color: #4b5563; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 2px solid #e5e7eb; padding-bottom: 8px;">Cast</h4>
        <ul style="list-style: none; padding: 0; margin: 0;">
            <?php foreach ($cast_credits as $credit): ?>
            <li style="padding: 8px 0; border-bottom: 1px solid #f3f4f6;">
                <a href="<?php echo htmlspecialchars($profile_base_url . (strpos($profile_base_url, '?') !== false ? '&' : '?') . 'id=' . $credit['person']['id']); ?>" 
                   style="color: #4f46e5; text-decoration: none; font-weight: 500;">
                    <?php echo htmlspecialchars($credit['person']['name']); ?>
                </a>
                <?php if (!empty($credit['role'])): ?>
                    <span style="color: #6b7280;"> as <?php echo htmlspecialchars($credit['role']); ?></span>
                <?php endif; ?>
                <?php if ($credit['is_equity']): ?>
                    <span style="color: #10b981; font-weight: 600;"> *</span>
                <?php endif; ?>
            </li>
            <?php endforeach; ?>
        </ul>
    </div>
    <?php endif; ?>
    
    <?php if (!empty($crew_credits)): ?>
    <div class="playbill-crew" style="margin-bottom: 30px;">
        <h4 style="font-size: 18px; font-weight: 600; margin-bottom: 15px; color: #4b5563; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 2px solid #e5e7eb; padding-bottom: 8px;">Crew</h4>
        <ul style="list-style: none; padding: 0; margin: 0;">
            <?php foreach ($crew_credits as $credit): ?>
            <li style="padding: 8px 0; border-bottom: 1px solid #f3f4f6;">
                <a href="<?php echo htmlspecialchars($profile_base_url . (strpos($profile_base_url, '?') !== false ? '&' : '?') . 'id=' . $credit['person']['id']); ?>" 
                   style="color: #4f46e5; text-decoration: none; font-weight: 500;">
                    <?php echo htmlspecialchars($credit['person']['name']); ?>
                </a>
                <?php if (!empty($credit['role'])): ?>
                    <span style="color: #6b7280;"> - <?php echo htmlspecialchars($credit['role']); ?></span>
                <?php endif; ?>
                <?php if ($credit['is_equity']): ?>
                    <span style="color: #10b981; font-weight: 600;"> *</span>
                <?php endif; ?>
            </li>
            <?php endforeach; ?>
        </ul>
    </div>
    <?php endif; ?>
    
    <?php if (!empty($creative_credits)): ?>
    <div class="playbill-creative" style="margin-bottom: 30px;">
        <h4 style="font-size: 18px; font-weight: 600; margin-bottom: 15px; color: #4b5563; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 2px solid #e5e7eb; padding-bottom: 8px;">Creative Team</h4>
        <ul style="list-style: none; padding: 0; margin: 0;">
            <?php foreach ($creative_credits as $credit): ?>
            <li style="padding: 8px 0; border-bottom: 1px solid #f3f4f6;">
                <a href="<?php echo htmlspecialchars($profile_base_url . (strpos($profile_base_url, '?') !== false ? '&' : '?') . 'id=' . $credit['person']['id']); ?>" 
                   style="color: #4f46e5; text-decoration: none; font-weight: 500;">
                    <?php echo htmlspecialchars($credit['person']['name']); ?>
                </a>
                <?php if (!empty($credit['role'])): ?>
                    <span style="color: #6b7280;"> - <?php echo htmlspecialchars($credit['role']); ?></span>
                <?php endif; ?>
                <?php if ($credit['is_equity']): ?>
                    <span style="color: #10b981; font-weight: 600;"> *</span>
                <?php endif; ?>
            </li>
            <?php endforeach; ?>
        </ul>
    </div>
    <?php endif; ?>
</div>

