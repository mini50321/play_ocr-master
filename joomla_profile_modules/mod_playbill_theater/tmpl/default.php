<?php
defined('_JEXEC') or die;

use Joomla\CMS\Factory;

$app = Factory::getApplication();
$input = $app->input;
$theater_id = $input->getInt('id', $params->get('theater_id', 0));

$api_base_url = $params->get('api_base_url', 'https://www.broadwayandmain.com/playbill_app/api/joomla');
$public_base_url = $params->get('public_base_url', 'https://www.broadwayandmain.com/playbill_app/public');
$profile_base_url = $params->get('profile_base_url', $public_base_url);
$actor_profile_url = $params->get('actor_profile_url', '');
$show_profile_url = $params->get('show_profile_url', '');
$module_enabled = $params->get('module_enabled', 1);

if (empty($actor_profile_url)) {
    $actor_profile_url = !empty($profile_base_url) ? $profile_base_url : $public_base_url;
}
if (empty($show_profile_url)) {
    $show_profile_url = !empty($profile_base_url) ? $profile_base_url : $public_base_url;
}

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
<style>
.playbill-theater-module img:not([src]),
.playbill-theater-module img[src=""],
.playbill-theater-module div:empty:not(#theater-map):not(.leaflet-container):not(.leaflet-pane),
.playbill-theater-module p:empty,
.playbill-theater-module span:empty,
.playbill-theater-module li:empty {
    display: none !important;
}
</style>
<script>
(function() {
    function cleanExcessiveBreaks() {
        const descriptionDiv = document.querySelector('.playbill-description-content');
        if (descriptionDiv) {
            let html = descriptionDiv.innerHTML;
            html = html.replace(/(<br\s*\/?>\s*){3,}/gi, '<br><br>');
            html = html.replace(/(<br\s*\/?>){3,}/gi, '<br><br>');
            html = html.replace(/&nbsp;/gi, ' ');
            html = html.replace(/(<br\s*\/?>\s*){2,}/gi, '<br><br>');
            descriptionDiv.innerHTML = html;
        }
    }
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', cleanExcessiveBreaks);
    } else {
        cleanExcessiveBreaks();
    }
    setTimeout(cleanExcessiveBreaks, 100);
    setTimeout(cleanExcessiveBreaks, 500);
})();
</script>
<div class="playbill-theater-module" style="margin: 20px 0; padding: 20px; border: 1px solid #e5e7eb; border-radius: 8px; background: #fff;">
    <h2 class="playbill-title" style="font-size: 28px; font-weight: bold; margin-bottom: 15px; color: #1f2937;">
        <?php echo htmlspecialchars($theater_data['name']); ?>
    </h2>
    
    <?php 
    $theater_address = isset($theater_data['address']) ? trim($theater_data['address']) : '';
    if (!empty($theater_address)): ?>
    <p style="color: #6b7280; margin-bottom: 10px; font-size: 16px;">
        <strong style="color: #1f2937;">Address:</strong> <?php echo htmlspecialchars($theater_address); ?>
    </p>
    <?php endif; ?>
    
    <?php 
    $clean_description = '';
    if (!empty($theater_data['description'])) {
        $clean_description = $theater_data['description'];
        $clean_description = preg_replace('/<br\s*\/?>\s*<br\s*\/?>/i', "\n", $clean_description);
        $clean_description = strip_tags($clean_description);
        $clean_description = html_entity_decode($clean_description, ENT_QUOTES, 'UTF-8');
        $clean_description = str_replace('&nbsp;', ' ', $clean_description);
        $clean_description = preg_replace('/\r\n|\r/', "\n", $clean_description);
        $clean_description = preg_replace('/\n{3,}/', "\n\n", $clean_description);
        $clean_description = preg_replace('/[ \t]+/', ' ', $clean_description);
        $clean_description = preg_replace('/\n /', "\n", $clean_description);
        $clean_description = preg_replace('/ \n/', "\n", $clean_description);
        $clean_description = trim($clean_description);
        
        $lines = explode("\n", $clean_description);
        $filtered_lines = [];
        $prev_empty = false;
        foreach ($lines as $line) {
            $line = trim($line);
            if (empty($line)) {
                if (!$prev_empty) {
                    $filtered_lines[] = '';
                    $prev_empty = true;
                }
            } else {
                $filtered_lines[] = $line;
                $prev_empty = false;
            }
        }
        $clean_description = implode("\n", $filtered_lines);
        $clean_description = trim($clean_description);
    }
    if (!empty($clean_description)): ?>
    <div style="margin-bottom: 30px; padding: 15px; background: #f9fafb; border-radius: 6px;">
        <div style="color: #6b7280; line-height: 1.6;" class="playbill-description-content">
            <?php 
            $final_description = preg_replace('/\n{3,}/', "\n\n", $clean_description);
            $final_description = preg_replace('/\n\n+/', "\n\n", $final_description);
            $output = nl2br(htmlspecialchars($final_description));
            $output = preg_replace('/(<br\s*\/?>\s*){3,}/i', '<br><br>', $output);
            echo $output;
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
    <?php
    $has_valid_productions = false;
    foreach ($show_item['productions'] as $prod_check) {
        if (!empty($prod_check['credits']) && is_array($prod_check['credits'])) {
            foreach ($prod_check['credits'] as $credit_check) {
                if (!empty($credit_check['category']) && !empty($credit_check['person']['name'])) {
                    $has_valid_productions = true;
                    break 2;
                }
            }
        }
    }
    if ($has_valid_productions): ?>
    <div class="playbill-show-item" style="margin-bottom: 40px; padding-bottom: 30px; border-bottom: 2px solid #f3f4f6;">
        <h4 style="font-size: 20px; font-weight: 600; margin-bottom: 15px; color: #4b5563;">
            <?php 
            $show_url = '';
            if (strpos($show_profile_url, 'index.php') !== false) {
                if (strpos($show_profile_url, '?') !== false) {
                    $show_url = $show_profile_url . '&id=' . $show_item['show']['id'] . '&type=show';
                } else {
                    $show_url = $show_profile_url . '?id=' . $show_item['show']['id'] . '&type=show';
                }
            } else {
                $show_url = rtrim($show_profile_url, '/') . '/show/' . $show_item['show']['id'];
            }
            ?>
            <a href="<?php echo htmlspecialchars($show_url); ?>" style="color: #4f46e5; text-decoration: none;">
                <?php echo htmlspecialchars($show_item['show']['title']); ?>
            </a>
        </h4>
        
        <?php foreach ($show_item['productions'] as $production): ?>
        <?php
        $credits_by_category = [];
        $all_production_credits = [];
        if (!empty($production['credits']) && is_array($production['credits'])) {
            foreach ($production['credits'] as $credit) {
                if (!empty($credit['category'])) {
                    $category = $credit['category'];
                    if (!isset($credits_by_category[$category])) {
                        $credits_by_category[$category] = [];
                    }
                    $credits_by_category[$category][] = $credit;
                }
                $all_production_credits[] = $credit;
            }
            usort($all_production_credits, function($a, $b) {
                $nameA = isset($a['person']['name']) ? strtolower($a['person']['name']) : '';
                $nameB = isset($b['person']['name']) ? strtolower($b['person']['name']) : '';
                return strcmp($nameA, $nameB);
            });
        }
        if (!empty($credits_by_category) || !empty($all_production_credits)): ?>
        <div style="margin-bottom: 20px;">
            <button onclick="showProductionView('category-<?php echo $production['id']; ?>')" id="view-category-btn-<?php echo $production['id']; ?>" style="padding: 8px 16px; margin-right: 8px; background: #4f46e5; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: 600; font-size: 13px;">By Category</button>
            <button onclick="showProductionView('alphabetical-<?php echo $production['id']; ?>')" id="view-alphabetical-btn-<?php echo $production['id']; ?>" style="padding: 8px 16px; background: #e5e7eb; color: #6b7280; border: none; border-radius: 4px; cursor: pointer; font-weight: 600; font-size: 13px;">Alphabetical</button>
        </div>
        <div id="category-view-<?php echo $production['id']; ?>">
        <?php if (!empty($credits_by_category)): ?>
        <div style="margin-bottom: 25px; padding: 15px; background: #fafafa; border-radius: 6px; border-left: 3px solid #4f46e5;">
            <p style="margin: 0 0 15px 0; color: #6b7280; font-size: 16px; font-weight: 600;">
                <?php echo (int)$production['year']; ?>
            </p>
            
            <?php foreach ($credits_by_category as $category => $credits): ?>
            <?php if (!empty($credits)): ?>
            <div style="margin-bottom: 20px;">
                <h5 style="font-size: 16px; font-weight: 600; margin-bottom: 10px; color: #4b5563; text-transform: uppercase; letter-spacing: 0.5px;">
                    <?php echo htmlspecialchars($category); ?>
                </h5>
                <ul style="list-style: none; padding: 0; margin: 0;">
                    <?php foreach ($credits as $credit): ?>
                    <?php if (!empty($credit['person']['name'])): ?>
                    <li style="padding: 8px 0; border-bottom: 1px solid #f3f4f6;">
                        <div>
                            <strong style="font-size: 15px; color: #1f2937;">
                                <?php 
                                $person_url = '';
                                if (strpos($actor_profile_url, 'index.php') !== false) {
                                    if (strpos($actor_profile_url, '?') !== false) {
                                        $person_url = $actor_profile_url . '&id=' . $credit['person']['id'] . '&type=actor';
                                    } else {
                                        $person_url = $actor_profile_url . '?id=' . $credit['person']['id'] . '&type=actor';
                                    }
                                } else {
                                    $person_url = rtrim($actor_profile_url, '/') . '/actor/' . $credit['person']['id'];
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
                    <?php endif; ?>
                    <?php endforeach; ?>
                </ul>
            </div>
            <?php endif; ?>
            <?php endforeach; ?>
            </div>
            
            <div id="alphabetical-view-<?php echo $production['id']; ?>" style="display: none;">
            <?php if (!empty($all_production_credits)): ?>
            <ul style="list-style: none; padding: 0; margin: 0;">
                <?php foreach ($all_production_credits as $credit): ?>
                <?php if (!empty($credit['person']['name'])): ?>
                <li style="padding: 8px 0; border-bottom: 1px solid #f3f4f6;">
                    <div>
                        <strong style="font-size: 15px; color: #1f2937;">
                            <?php 
                            $person_url = '';
                            if (strpos($actor_profile_url, 'index.php') !== false) {
                                if (strpos($actor_profile_url, '?') !== false) {
                                    $person_url = $actor_profile_url . '&id=' . $credit['person']['id'] . '&type=actor';
                                } else {
                                    $person_url = $actor_profile_url . '?id=' . $credit['person']['id'] . '&type=actor';
                                }
                            } else {
                                $person_url = rtrim($actor_profile_url, '/') . '/actor/' . $credit['person']['id'];
                            }
                            ?>
                            <a href="<?php echo htmlspecialchars($person_url); ?>" style="color: #4f46e5; text-decoration: none;">
                                <?php echo htmlspecialchars($credit['person']['name']); ?>
                            </a>
                        </strong>
                        <?php if (!empty($credit['role']) && $credit['role'] !== $credit['category']): ?>
                            <span style="color: #6b7280; margin-left: 8px;">as <?php echo htmlspecialchars($credit['role']); ?></span>
                        <?php endif; ?>
                        <?php if (!empty($credit['category'])): ?>
                            <span style="color: #9ca3af; margin-left: 8px; font-size: 13px;">(<?php echo htmlspecialchars($credit['category']); ?>)</span>
                        <?php endif; ?>
                        <?php if ($credit['is_equity']): ?>
                            <span style="color: #10b981; font-weight: 600; margin-left: 5px;">*</span>
                        <?php endif; ?>
                    </div>
                </li>
                <?php endif; ?>
                <?php endforeach; ?>
            </ul>
            <?php endif; ?>
            </div>
        </div>
        <?php endif; ?>
        <?php endforeach; ?>
    </div>
    <?php endif; ?>
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
<script>
function showProductionView(view) {
    const parts = view.split('-');
    const viewType = parts[0];
    const productionId = parts.slice(1).join('-');
    
    const categoryView = document.getElementById('category-view-' + productionId);
    const alphabeticalView = document.getElementById('alphabetical-view-' + productionId);
    const categoryBtn = document.getElementById('view-category-btn-' + productionId);
    const alphabeticalBtn = document.getElementById('view-alphabetical-btn-' + productionId);
    
    if (viewType === 'category') {
        categoryView.style.display = 'block';
        alphabeticalView.style.display = 'none';
        categoryBtn.style.background = '#4f46e5';
        categoryBtn.style.color = 'white';
        alphabeticalBtn.style.background = '#e5e7eb';
        alphabeticalBtn.style.color = '#6b7280';
    } else {
        categoryView.style.display = 'none';
        alphabeticalView.style.display = 'block';
        categoryBtn.style.background = '#e5e7eb';
        categoryBtn.style.color = '#6b7280';
        alphabeticalBtn.style.background = '#4f46e5';
        alphabeticalBtn.style.color = 'white';
    }
}
</script>

