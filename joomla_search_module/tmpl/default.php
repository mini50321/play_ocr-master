<?php
defined('_JEXEC') or die;

use Joomla\CMS\Factory;
use Joomla\CMS\Uri\Uri;

$api_base_url = $params->get('api_base_url', 'https://www.broadwayandmain.com/playbill_app/api/joomla');
$public_base_url = $params->get('public_base_url', 'https://www.broadwayandmain.com/playbill_app/public');
$profile_base_url = $params->get('profile_base_url', '');
$actor_profile_url = $params->get('actor_profile_url', '');
$show_profile_url = $params->get('show_profile_url', '');
$theater_profile_url = $params->get('theater_profile_url', '');
$results_page_id = $params->get('results_page_id', 0);
$module_enabled = $params->get('module_enabled', 1);

if (empty($actor_profile_url)) {
    $actor_profile_url = !empty($profile_base_url) ? $profile_base_url : $public_base_url;
}
if (empty($show_profile_url)) {
    $show_profile_url = !empty($profile_base_url) ? $profile_base_url : $public_base_url;
}
if (empty($theater_profile_url)) {
    $theater_profile_url = !empty($profile_base_url) ? $profile_base_url : $public_base_url;
}

if (!$module_enabled) {
    return;
}

$app = Factory::getApplication();
$input = $app->input;
$current_query = $input->getString('playbill_q', '');
$current_filter = $input->getString('playbill_type', 'all');

$results = null;
if (!empty($current_query)) {
    $results = ModPlaybillSearchHelper::performSearch($current_query, $api_base_url, $current_filter);
}

$current_uri = Uri::getInstance();
$is_profile_page = $input->getInt('id', 0) > 0 && in_array($input->getString('type', ''), ['actor', 'show', 'theater']);

if ($results_page_id) {
    $search_url = 'index.php?Itemid=' . $results_page_id;
} elseif ($is_profile_page) {
    $menu = $app->getMenu();
    $home = $menu->getDefault();
    $search_url = $home ? 'index.php?Itemid=' . $home->id : 'index.php';
} else {
    $search_url = $current_uri->toString(['path', 'query']);
}

?>
<div class="playbill-search-module" style="margin: 20px 0;">
    <form method="GET" action="<?php echo htmlspecialchars($search_url); ?>" class="playbill-search-form">
        <input type="hidden" name="playbill_type" value="<?php echo htmlspecialchars($current_filter); ?>" id="playbill-type-hidden">
        
        <div style="display: flex; gap: 10px; margin-bottom: 15px; align-items: center; flex-wrap: nowrap;">
            <input type="text" 
                   name="playbill_q" 
                   value="<?php echo htmlspecialchars($current_query); ?>" 
                   placeholder="Search Playbill Database: actors, shows, theaters only..." 
                   class="playbill-search-input"
                   style="flex: 1; padding: 10px; border: 1px solid #d1d5db; border-radius: 4px; font-size: 16px; height: 44px; box-sizing: border-box; min-width: 0;"
                   id="playbill-search-input"
                   title="Search ONLY Playbill database (actors, shows, theaters). Does NOT search Joomla articles.">
            
            <select name="playbill_type" 
                    id="playbill-filter-type" 
                    style="padding: 8px 12px; border: 1px solid #d1d5db; border-radius: 4px; font-size: 14px; height: 44px; box-sizing: border-box; width: auto; min-width: 80px; max-width: 120px; flex-shrink: 0; white-space: nowrap;">
                <option value="all" <?php echo $current_filter === 'all' ? 'selected' : ''; ?>>All</option>
                <option value="actors" <?php echo $current_filter === 'actors' ? 'selected' : ''; ?>>Actors</option>
                <option value="shows" <?php echo $current_filter === 'shows' ? 'selected' : ''; ?>>Shows</option>
                <option value="theaters" <?php echo $current_filter === 'theaters' ? 'selected' : ''; ?>>Theaters</option>
            </select>
            
            <button type="submit" 
                    class="playbill-search-button"
                    style="padding: 10px 20px; background: #4f46e5; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; font-weight: 500; white-space: nowrap; height: 44px; box-sizing: border-box; flex-shrink: 0;">
                Search
            </button>
        </div>
    </form>
    
    <?php if ($results && !empty($current_query)): ?>
    <div id="playbill-search-modal" class="playbill-modal" style="display: block; position: fixed; z-index: 10000; left: 0; top: 0; width: 100%; height: 100%; overflow: auto; background-color: rgba(0,0,0,0.6);">
        <div class="playbill-modal-content" style="background-color: #ffffff; margin: 3% auto; padding: 0; border: none; width: 90%; max-width: 900px; border-radius: 12px; box-shadow: 0 10px 40px rgba(0,0,0,0.3); max-height: 85vh; overflow-y: auto; position: relative;">
            <div style="padding: 24px; border-bottom: 2px solid #e5e7eb; display: flex; justify-content: space-between; align-items: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px 12px 0 0; position: sticky; top: 0; z-index: 1;">
                <h2 style="margin: 0; font-size: 24px; font-weight: 600; color: #ffffff;">Playbill Database Search Results for "<?php echo htmlspecialchars($current_query); ?>"</h2>
                <p style="margin: 8px 0 0 0; font-size: 14px; color: rgba(255,255,255,0.9);">Showing results from Playbill database only (actors, shows, theaters)</p>
                <span class="playbill-modal-close" style="color: #ffffff; font-size: 32px; font-weight: bold; cursor: pointer; line-height: 24px; opacity: 0.9; transition: opacity 0.2s;" onmouseover="this.style.opacity='1'" onmouseout="this.style.opacity='0.9'">&times;</span>
            </div>
            <div style="padding: 24px; background: #ffffff;">
    <div class="playbill-search-results" style="margin-top: 20px;">
        <?php 
        $filtered_actors = [];
        if (!empty($results['actors'])) {
            foreach ($results['actors'] as $actor) {
                $credits_count = (int)($actor['credits_count'] ?? 0);
                if ($credits_count > 0) {
                    $filtered_actors[] = $actor;
                }
            }
        }
        if (!empty($filtered_actors)): ?>
        <div class="playbill-results-section" style="margin-bottom: 30px;">
            <h3 style="font-size: 22px; font-weight: 600; margin-bottom: 20px; color: #1f2937; border-bottom: 3px solid #667eea; padding-bottom: 12px;">
                Actors (<?php echo count($filtered_actors); ?>)
            </h3>
            <ul style="list-style: none; padding: 0; margin: 0;">
                <?php foreach ($filtered_actors as $actor): ?>
                <li style="padding: 14px 16px; border-bottom: 1px solid #f3f4f6; border-left: 3px solid transparent; transition: all 0.2s; background: #fafafa;" onmouseover="this.style.borderLeftColor='#667eea'; this.style.background='#f0f0f0';" onmouseout="this.style.borderLeftColor='transparent'; this.style.background='#fafafa';">
                    <a href="<?php 
                        if (strpos($actor_profile_url, 'index.php') !== false || strpos($actor_profile_url, '?') !== false) {
                            $separator = (strpos($actor_profile_url, '?') !== false) ? '&' : '?';
                            echo htmlspecialchars($actor_profile_url . $separator . 'id=' . $actor['id'] . '&type=actor');
                        } else {
                            echo htmlspecialchars($actor_profile_url . '/actor/' . $actor['id']);
                        }
                    ?>" 
                       target="_blank" 
                       rel="noopener noreferrer"
                       style="color: #4f46e5; text-decoration: none; font-weight: 500; font-size: 16px; display: block;">
                        <?php echo htmlspecialchars($actor['name']); ?>
                        <span style="color: #6b7280; font-size: 14px; margin-left: 10px; font-weight: normal;">
                            (<?php echo (int)$actor['credits_count']; ?> credits)
                        </span>
                    </a>
                </li>
                <?php endforeach; ?>
            </ul>
        </div>
        <?php endif; ?>
        
        <?php 
        $filtered_shows = [];
        if (!empty($results['shows'])) {
            foreach ($results['shows'] as $show) {
                $productions_count = (int)($show['productions_count'] ?? 0);
                if ($productions_count > 0) {
                    $filtered_shows[] = $show;
                }
            }
        }
        if (!empty($filtered_shows)): ?>
        <div class="playbill-results-section" style="margin-bottom: 30px;">
            <h3 style="font-size: 22px; font-weight: 600; margin-bottom: 20px; color: #1f2937; border-bottom: 3px solid #667eea; padding-bottom: 12px;">
                Shows (<?php echo count($filtered_shows); ?>)
            </h3>
            <ul style="list-style: none; padding: 0; margin: 0;">
                <?php foreach ($filtered_shows as $show): ?>
                <?php 
                    if (!isset($show['id']) || empty($show['id'])) {
                        continue;
                    }
                    $show_id = (int)$show['id'];
                    if ($show_id <= 0) {
                        continue;
                    }
                    $productions_count = (int)($show['productions_count'] ?? 0);
                    if ($productions_count <= 0) {
                        continue;
                    }
                    if (strpos($show_profile_url, 'index.php') !== false || strpos($show_profile_url, '?') !== false) {
                        $separator = (strpos($show_profile_url, '?') !== false) ? '&' : '?';
                        $show_link = $show_profile_url . $separator . 'id=' . $show_id . '&type=show';
                    } else {
                        $show_link = rtrim($show_profile_url, '/') . '/show/' . $show_id;
                    }
                ?>
                <li style="padding: 14px 16px; border-bottom: 1px solid #f3f4f6; border-left: 3px solid transparent; transition: all 0.2s; background: #fafafa;" onmouseover="this.style.borderLeftColor='#667eea'; this.style.background='#f0f0f0';" onmouseout="this.style.borderLeftColor='transparent'; this.style.background='#fafafa';">
                    <a href="<?php echo htmlspecialchars($show_link); ?>" 
                       target="_blank" 
                       rel="noopener noreferrer"
                       style="color: #4f46e5; text-decoration: none; font-weight: 500; font-size: 16px; display: block;"
                       title="Playbill Show ID: <?php echo $show_id; ?>">
                        <?php echo htmlspecialchars($show['title'] ?? 'Unknown Show'); ?>
                        <span style="color: #6b7280; font-size: 14px; margin-left: 10px; font-weight: normal;">
                            (<?php echo $productions_count; ?> production(s))
                        </span>
                    </a>
                </li>
                <?php endforeach; ?>
            </ul>
        </div>
        <?php endif; ?>
        
        <?php 
        $filtered_theaters = [];
        if (!empty($results['theaters'])) {
            foreach ($results['theaters'] as $theater) {
                $productions_count = (int)($theater['productions_count'] ?? 0);
                if ($productions_count > 0) {
                    $filtered_theaters[] = $theater;
                }
            }
        }
        if (!empty($filtered_theaters)): ?>
        <div class="playbill-results-section" style="margin-bottom: 30px;">
            <h3 style="font-size: 22px; font-weight: 600; margin-bottom: 20px; color: #1f2937; border-bottom: 3px solid #667eea; padding-bottom: 12px;">
                Theaters (<?php echo count($filtered_theaters); ?>)
            </h3>
            <ul style="list-style: none; padding: 0; margin: 0;">
                <?php foreach ($filtered_theaters as $theater): ?>
                <?php 
                    $theater_productions_count = (int)($theater['productions_count'] ?? 0);
                    if ($theater_productions_count <= 0) {
                        continue;
                    }
                ?>
                <li style="padding: 14px 16px; border-bottom: 1px solid #f3f4f6; border-left: 3px solid transparent; transition: all 0.2s; background: #fafafa;" onmouseover="this.style.borderLeftColor='#667eea'; this.style.background='#f0f0f0';" onmouseout="this.style.borderLeftColor='transparent'; this.style.background='#fafafa';">
                    <a href="<?php 
                        if (strpos($theater_profile_url, 'index.php') !== false || strpos($theater_profile_url, '?') !== false) {
                            $separator = (strpos($theater_profile_url, '?') !== false) ? '&' : '?';
                            echo htmlspecialchars($theater_profile_url . $separator . 'id=' . $theater['id'] . '&type=theater');
                        } else {
                            echo htmlspecialchars($theater_profile_url . '/theater/' . $theater['id']);
                        }
                    ?>" 
                       target="_blank" 
                       rel="noopener noreferrer"
                       style="color: #4f46e5; text-decoration: none; font-weight: 500; font-size: 16px; display: block;">
                        <?php echo htmlspecialchars($theater['name']); ?>
                        <span style="color: #6b7280; font-size: 14px; margin-left: 10px; font-weight: normal;">
                            (<?php echo $theater_productions_count; ?> production(s))
                        </span>
                    </a>
                </li>
                <?php endforeach; ?>
            </ul>
        </div>
        <?php endif; ?>
        
        <?php if (empty($filtered_actors) && empty($filtered_shows) && empty($filtered_theaters)): ?>
        <div style="padding: 40px; text-align: center; color: #6b7280;">
            <p style="font-size: 18px;">No results found for "<?php echo htmlspecialchars($current_query); ?>"</p>
        </div>
        <?php endif; ?>
            </div>
        </div>
    </div>
    <?php endif; ?>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    const filterType = document.getElementById('playbill-filter-type');
    const hiddenType = document.getElementById('playbill-type-hidden');
    
    if (filterType && hiddenType) {
        filterType.addEventListener('change', function() {
            hiddenType.value = this.value;
        });
    }
    
    const modal = document.getElementById('playbill-search-modal');
    const closeBtn = document.querySelector('.playbill-modal-close');
    
    if (closeBtn && modal) {
        closeBtn.addEventListener('click', function() {
            modal.style.display = 'none';
        });
    }
    
    if (modal) {
        window.addEventListener('click', function(event) {
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        });
    }
    
    const searchForm = document.querySelector('.playbill-search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            const query = document.getElementById('playbill-search-input').value.trim();
            if (query) {
                setTimeout(function() {
                    const modal = document.getElementById('playbill-search-modal');
                    if (modal) {
                        modal.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    }
                }, 100);
            }
        });
    }
});
</script>

