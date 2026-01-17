<?php
defined('_JEXEC') or die;

use Joomla\CMS\Factory;

$app = Factory::getApplication();
$input = $app->input;
$theater_id = $input->getInt('id', $params->get('theater_id', 0));

$api_base_url = $params->get('api_base_url', 'https://www.broadwayandmain.com/playbill_app/api/joomla');
$public_base_url = $params->get('public_base_url', 'https://www.broadwayandmain.com/playbill_app/public');
$profile_base_url = $params->get('profile_base_url', $public_base_url);
$module_enabled = $params->get('module_enabled', 1);

if (!$module_enabled || empty($theater_id)) {
    return;
}

$theater_data = ModPlaybillTheaterHelper::getTheaterData($theater_id, $api_base_url, $public_base_url);

if (!$theater_data) {
    if (Factory::getApplication()->get('debug')) {
        echo '<div class="playbill-error" style="padding: 10px; background: #fee; border: 1px solid #fcc; color: #c00; border-radius: 4px; margin: 10px 0;">';
        echo 'Playbill Theater Module: Theater not found or error loading data for Theater ID ' . htmlspecialchars($theater_id) . '.';
        echo '</div>';
    }
    return;
}

?>
<div class="playbill-theater-module" style="margin: 20px 0; padding: 20px; border: 1px solid #e5e7eb; border-radius: 8px; background: #fff;">
    <h2 class="playbill-title" style="font-size: 28px; font-weight: bold; margin-bottom: 15px; color: #1f2937;">
        <?php echo htmlspecialchars($theater_data['name']); ?>
    </h2>
    
    <?php if (!empty($theater_data['address'])): ?>
    <p style="color: #6b7280; margin-bottom: 10px; font-size: 16px;">
        <strong style="color: #1f2937;">Address:</strong> <?php echo htmlspecialchars($theater_data['address']); ?>
    </p>
    <?php endif; ?>
    
    <?php if (!empty($theater_data['description'])): ?>
    <div style="margin-bottom: 30px; padding: 15px; background: #f9fafb; border-radius: 6px;">
        <div style="color: #6b7280; line-height: 1.6;">
            <?php 
            $clean_description = strip_tags($theater_data['description']);
            $clean_description = html_entity_decode($clean_description, ENT_QUOTES, 'UTF-8');
            echo nl2br(htmlspecialchars($clean_description)); 
            ?>
        </div>
    </div>
    <?php endif; ?>
    
    <?php if (!empty($theater_data['latitude']) && !empty($theater_data['longitude'])): ?>
    <div style="margin-bottom: 30px; padding: 15px; background: #f9fafb; border-radius: 6px;">
        <h3 style="font-size: 20px; font-weight: 600; margin-bottom: 15px; color: #1f2937;">Location</h3>
        <div id="theater-map" style="height: 400px; width: 100%; border-radius: 8px;"></div>
    </div>
    <?php endif; ?>
    
    <?php if (!empty($theater_data['shows'])): ?>
    <h3 style="font-size: 22px; font-weight: 600; margin-bottom: 20px; color: #1f2937; border-bottom: 2px solid #e5e7eb; padding-bottom: 10px;">
        Productions
    </h3>
    
    <?php foreach ($theater_data['shows'] as $show_item): ?>
    <div class="playbill-show-item" style="margin-bottom: 40px; padding-bottom: 30px; border-bottom: 2px solid #f3f4f6;">
        <h4 style="font-size: 20px; font-weight: 600; margin-bottom: 15px; color: #4b5563;">
            <?php 
            $show_url = '';
            if (strpos($profile_base_url, 'index.php') !== false || strpos($profile_base_url, '?') !== false) {
                $separator = (strpos($profile_base_url, '?') !== false) ? '&' : '?';
                $show_url = $profile_base_url . $separator . 'id=' . $show_item['show']['id'] . '&type=show';
            } else {
                $show_url = $profile_base_url . '/show/' . $show_item['show']['id'];
            }
            ?>
            <a href="<?php echo htmlspecialchars($show_url); ?>" style="color: #4f46e5; text-decoration: none;">
                <?php echo htmlspecialchars($show_item['show']['title']); ?>
            </a>
        </h4>
        
        <?php foreach ($show_item['productions'] as $production): ?>
        <div style="margin-bottom: 25px; padding: 15px; background: #fafafa; border-radius: 6px; border-left: 3px solid #4f46e5;">
            <p style="margin: 0 0 15px 0; color: #6b7280; font-size: 16px; font-weight: 600;">
                <?php echo (int)$production['year']; ?>
            </p>
            
            <?php
            $credits_by_category = [];
            foreach ($production['credits'] as $credit) {
                $category = $credit['category'];
                if (!isset($credits_by_category[$category])) {
                    $credits_by_category[$category] = [];
                }
                $credits_by_category[$category][] = $credit;
            }
            ?>
            
            <?php if (!empty($credits_by_category)): ?>
            <?php foreach ($credits_by_category as $category => $credits): ?>
            <div style="margin-bottom: 20px;">
                <h5 style="font-size: 16px; font-weight: 600; margin-bottom: 10px; color: #4b5563; text-transform: uppercase; letter-spacing: 0.5px;">
                    <?php echo htmlspecialchars($category); ?>
                </h5>
                <ul style="list-style: none; padding: 0; margin: 0;">
                    <?php foreach ($credits as $credit): ?>
                    <li style="padding: 8px 0; border-bottom: 1px solid #f3f4f6;">
                        <div>
                            <strong style="font-size: 15px; color: #1f2937;">
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
                    </li>
                    <?php endforeach; ?>
                </ul>
            </div>
            <?php endforeach; ?>
            <?php endif; ?>
        </div>
        <?php endforeach; ?>
    </div>
    <?php endforeach; ?>
    <?php else: ?>
    <p style="color: #6b7280; padding: 20px; text-align: center;">No productions found for this theater.</p>
    <?php endif; ?>
</div>

<?php if (!empty($theater_data['latitude']) && !empty($theater_data['longitude'])): ?>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
(function() {
    const theaterLat = <?php echo json_encode($theater_data['latitude']); ?>;
    const theaterLng = <?php echo json_encode($theater_data['longitude']); ?>;
    const theaterName = <?php echo json_encode($theater_data['name']); ?>;
    const theaterAddress = <?php echo json_encode($theater_data['address'] ?? ''); ?>;
    const theaterCity = <?php echo json_encode($theater_data['city'] ?? ''); ?>;
    const theaterState = <?php echo json_encode($theater_data['state'] ?? ''); ?>;
    
    if (theaterLat && theaterLng) {
        const map = L.map('theater-map').setView([parseFloat(theaterLat), parseFloat(theaterLng)], 15);
        
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);
        
        const marker = L.marker([parseFloat(theaterLat), parseFloat(theaterLng)]).addTo(map);
        let popupContent = '<div style="padding: 8px;"><strong>' + theaterName + '</strong>';
        if (theaterAddress) {
            popupContent += '<br><span style="color: #6b7280;">' + theaterAddress + '</span>';
        }
        if (theaterCity || theaterState) {
            popupContent += '<br><span style="color: #6b7280;">' + theaterCity + (theaterCity && theaterState ? ', ' : '') + theaterState + '</span>';
        }
        popupContent += '</div>';
        marker.bindPopup(popupContent);
    }
})();
</script>
<?php endif; ?>

