<?php
defined('_JEXEC') or die;

use Joomla\CMS\Factory;
use Joomla\CMS\Uri\Uri;

$api_base_url = $params->get('api_base_url', 'https://www.broadwayandmain.com/playbill_app/api/joomla');
$public_base_url = $params->get('public_base_url', 'https://www.broadwayandmain.com/playbill_app/public');
$profile_base_url = $params->get('profile_base_url', '');
$results_page_id = $params->get('results_page_id', 0);
$module_enabled = $params->get('module_enabled', 1);

if (empty($profile_base_url)) {
    $profile_base_url = $public_base_url;
}

if (!$module_enabled) {
    return;
}

$app = Factory::getApplication();
$input = $app->input;
$current_query = $input->getString('playbill_q', '');
$current_filter = $input->getString('playbill_type', 'all');
$current_equity = $input->getString('playbill_equity', 'all');

$results = null;
if (!empty($current_query)) {
    $results = ModPlaybillSearchHelper::performSearch($current_query, $api_base_url, $current_filter, $current_equity);
}

$current_uri = Uri::getInstance();
$search_url = $results_page_id 
    ? 'index.php?Itemid=' . $results_page_id 
    : $current_uri->toString(['path', 'query']);

?>
<div class="playbill-search-module" style="margin: 20px 0;">
    <form method="GET" action="<?php echo htmlspecialchars($search_url); ?>" class="playbill-search-form">
        <input type="hidden" name="playbill_type" value="<?php echo htmlspecialchars($current_filter); ?>" id="playbill-type-hidden">
        <input type="hidden" name="playbill_equity" value="<?php echo htmlspecialchars($current_equity); ?>" id="playbill-equity-hidden">
        
        <div style="display: flex; gap: 10px; margin-bottom: 15px; align-items: flex-end; flex-wrap: wrap;">
            <input type="text" 
                   name="playbill_q" 
                   value="<?php echo htmlspecialchars($current_query); ?>" 
                   placeholder="Search actors, shows, theaters..." 
                   class="playbill-search-input"
                   style="flex: 1; min-width: 200px; padding: 10px; border: 1px solid #d1d5db; border-radius: 4px; font-size: 16px; height: 44px; box-sizing: border-box;"
                   id="playbill-search-input">
            
            <div style="display: flex; gap: 10px; align-items: flex-end;">
                <div>
                    <select name="playbill_type" 
                            id="playbill-filter-type" 
                            style="padding: 8px; border: 1px solid #d1d5db; border-radius: 4px; font-size: 14px; height: 44px; box-sizing: border-box;">
                        <option value="all" <?php echo $current_filter === 'all' ? 'selected' : ''; ?>>All</option>
                        <option value="actors" <?php echo $current_filter === 'actors' ? 'selected' : ''; ?>>Actors</option>
                        <option value="shows" <?php echo $current_filter === 'shows' ? 'selected' : ''; ?>>Shows</option>
                        <option value="theaters" <?php echo $current_filter === 'theaters' ? 'selected' : ''; ?>>Theaters</option>
                    </select>
                </div>
                
                <div>
                    <select name="playbill_equity" 
                            id="playbill-filter-equity" 
                            style="padding: 8px; border: 1px solid #d1d5db; border-radius: 4px; font-size: 14px; height: 44px; box-sizing: border-box;">
                        <option value="all" <?php echo $current_equity === 'all' ? 'selected' : ''; ?>>All</option>
                        <option value="equity" <?php echo $current_equity === 'equity' ? 'selected' : ''; ?>>Equity Only</option>
                        <option value="non-equity" <?php echo $current_equity === 'non-equity' ? 'selected' : ''; ?>>Non-Equity Only</option>
                    </select>
                </div>
            </div>
            
            <button type="submit" 
                    class="playbill-search-button"
                    style="padding: 10px 20px; background: #4f46e5; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; font-weight: 500; white-space: nowrap; height: 44px; box-sizing: border-box;">
                Search
            </button>
        </div>
    </form>
    
    <?php if ($results && !empty($current_query)): ?>
    <div class="playbill-search-results" style="margin-top: 20px;">
        <?php if (!empty($results['actors'])): ?>
        <div class="playbill-results-section" style="margin-bottom: 30px;">
            <h3 style="font-size: 20px; font-weight: 600; margin-bottom: 15px; color: #1f2937; border-bottom: 2px solid #e5e7eb; padding-bottom: 8px;">
                Actors (<?php echo count($results['actors']); ?>)
            </h3>
            <ul style="list-style: none; padding: 0; margin: 0;">
                <?php foreach ($results['actors'] as $actor): ?>
                <li style="padding: 12px 0; border-bottom: 1px solid #f3f4f6;">
                    <a href="<?php 
                        if (strpos($profile_base_url, 'index.php') !== false || strpos($profile_base_url, '?') !== false) {
                            echo htmlspecialchars($profile_base_url . (strpos($profile_base_url, '?') !== false ? '&' : '?') . 'id=' . $actor['id']);
                        } else {
                            echo htmlspecialchars($profile_base_url . '/actor/' . $actor['id']);
                        }
                    ?>" 
                       style="color: #4f46e5; text-decoration: none; font-weight: 500; font-size: 16px;">
                        <?php echo htmlspecialchars($actor['name']); ?>
                    </a>
                    <span style="color: #6b7280; font-size: 14px; margin-left: 10px;">
                        (<?php echo (int)$actor['credits_count']; ?> credits)
                    </span>
                </li>
                <?php endforeach; ?>
            </ul>
        </div>
        <?php endif; ?>
        
        <?php if (!empty($results['shows'])): ?>
        <div class="playbill-results-section" style="margin-bottom: 30px;">
            <h3 style="font-size: 20px; font-weight: 600; margin-bottom: 15px; color: #1f2937; border-bottom: 2px solid #e5e7eb; padding-bottom: 8px;">
                Shows (<?php echo count($results['shows']); ?>)
            </h3>
            <ul style="list-style: none; padding: 0; margin: 0;">
                <?php foreach ($results['shows'] as $show): ?>
                <li style="padding: 12px 0; border-bottom: 1px solid #f3f4f6;">
                    <a href="<?php 
                        if (strpos($profile_base_url, 'index.php') !== false || strpos($profile_base_url, '?') !== false) {
                            echo htmlspecialchars($profile_base_url . '/show' . (strpos($profile_base_url, '?') !== false ? '&' : '?') . 'id=' . $show['id']);
                        } else {
                            echo htmlspecialchars($profile_base_url . '/show/' . $show['id']);
                        }
                    ?>" 
                       style="color: #4f46e5; text-decoration: none; font-weight: 500; font-size: 16px;">
                        <?php echo htmlspecialchars($show['title']); ?>
                    </a>
                    <span style="color: #6b7280; font-size: 14px; margin-left: 10px;">
                        (<?php echo (int)$show['productions_count']; ?> production(s))
                    </span>
                </li>
                <?php endforeach; ?>
            </ul>
        </div>
        <?php endif; ?>
        
        <?php if (!empty($results['theaters'])): ?>
        <div class="playbill-results-section" style="margin-bottom: 30px;">
            <h3 style="font-size: 20px; font-weight: 600; margin-bottom: 15px; color: #1f2937; border-bottom: 2px solid #e5e7eb; padding-bottom: 8px;">
                Theaters (<?php echo count($results['theaters']); ?>)
            </h3>
            <ul style="list-style: none; padding: 0; margin: 0;">
                <?php foreach ($results['theaters'] as $theater): ?>
                <li style="padding: 12px 0; border-bottom: 1px solid #f3f4f6;">
                    <a href="<?php 
                        if (strpos($profile_base_url, 'index.php') !== false || strpos($profile_base_url, '?') !== false) {
                            echo htmlspecialchars($profile_base_url . '/theater' . (strpos($profile_base_url, '?') !== false ? '&' : '?') . 'id=' . $theater['id']);
                        } else {
                            echo htmlspecialchars($profile_base_url . '/theater/' . $theater['id']);
                        }
                    ?>" 
                       style="color: #4f46e5; text-decoration: none; font-weight: 500; font-size: 16px;">
                        <?php echo htmlspecialchars($theater['name']); ?>
                    </a>
                    <span style="color: #6b7280; font-size: 14px; margin-left: 10px;">
                        (<?php echo (int)$theater['productions_count']; ?> production(s))
                    </span>
                </li>
                <?php endforeach; ?>
            </ul>
        </div>
        <?php endif; ?>
        
        <?php if (empty($results['actors']) && empty($results['shows']) && empty($results['theaters'])): ?>
        <div style="padding: 20px; text-align: center; color: #6b7280;">
            <p>No results found for "<?php echo htmlspecialchars($current_query); ?>"</p>
        </div>
        <?php endif; ?>
    </div>
    <?php endif; ?>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    const filterType = document.getElementById('playbill-filter-type');
    const filterEquity = document.getElementById('playbill-filter-equity');
    const hiddenType = document.getElementById('playbill-type-hidden');
    const hiddenEquity = document.getElementById('playbill-equity-hidden');
    
    if (filterType) {
        filterType.addEventListener('change', function() {
            hiddenType.value = this.value;
        });
    }
    
    if (filterEquity) {
        filterEquity.addEventListener('change', function() {
            hiddenEquity.value = this.value;
        });
    }
});
</script>

