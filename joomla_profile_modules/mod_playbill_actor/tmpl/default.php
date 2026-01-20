<?php
defined('_JEXEC') or die;

use Joomla\CMS\Factory;

echo '<!-- PLAYBILL ACTOR MODULE LOADED -->';
echo '<style>
.playbill-actor-grid {
    display: flex;
    flex-direction: column;
    gap: 24px;
}
.playbill-theaters-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 24px;
}
@media (min-width: 1024px) {
    .playbill-actor-grid {
        display: flex;
        flex-direction: column;
        gap: 24px;
    }
    .playbill-theaters-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 24px;
    }
}
</style>';
echo '<div id="playbill-actor-module-container" style="min-height: 1px;">';

try {
    if (!isset($params)) {
        echo '<div class="playbill-error" style="padding: 10px; background: #fee; border: 1px solid #fcc; color: #c00; border-radius: 4px; margin: 10px 0;">';
        echo 'Playbill Actor Module: Module parameters not available.';
        echo '</div>';
        echo '</div>';
        return;
    }
    
    $app = Factory::getApplication();
    $input = $app->input;
    $url_type = $input->getString('type', '');
    $url_id = $input->getInt('id', 0);
    $has_url_params = $input->get('playbill_q', null) !== null || $input->get('playbill_type', null) !== null;
    
    $raw_id = $input->get('id', null, 'raw');
    $all_get_params = $input->get->getArray();
    
    echo '<!-- DEBUG: url_type=' . htmlspecialchars($url_type) . ', url_id=' . htmlspecialchars($url_id) . ', raw_id=' . htmlspecialchars($raw_id ?? 'null') . ' -->';
    echo '<!-- DEBUG: All GET params: ' . htmlspecialchars(json_encode($all_get_params)) . ' -->';
    
    if ($url_type === 'actor' && $url_id > 0) {
        $actor_id = $url_id;
    } elseif ($url_id > 0 && empty($url_type) && !$has_url_params) {
        $actor_id = $url_id;
    } elseif (!$has_url_params) {
        $actor_id = $params->get('actor_id', 0);
    } else {
        $actor_id = 0;
    }

$api_base_url = $params->get('api_base_url', 'https://www.broadwayandmain.com/playbill_app/api/joomla');
$public_base_url = $params->get('public_base_url', 'https://www.broadwayandmain.com/playbill_app/public');
$show_profile_url = $params->get('show_profile_url', '');
$theater_profile_url = $params->get('theater_profile_url', '');
$module_enabled = $params->get('module_enabled', 1);

if (empty($show_profile_url)) {
    $show_profile_url = $public_base_url;
}
if (empty($theater_profile_url)) {
    $theater_profile_url = $public_base_url;
}

echo '<!-- Playbill Actor Module START: Actor ID = ' . htmlspecialchars($actor_id) . ' -->';

if (!$module_enabled) {
    echo '<!-- Playbill Actor Module is disabled -->';
    echo '</div>';
    return;
}

if (empty($actor_id)) {
    $playbill_q = $input->getString('playbill_q', '');
    if (!empty($playbill_q)) {
        echo '<!-- Playbill Actor Module: search request with no actor id, module hidden -->';
        echo '</div>';
        return;
    }
    echo '<div class="playbill-error" style="padding: 10px; background: #fee; border: 1px solid #fcc; color: #c00; border-radius: 4px; margin: 10px 0;">';
    echo '<strong>Playbill Actor Module Error</strong><br>';
    echo 'No Actor ID provided. Please provide ?id=XXX&type=actor in the URL.';
    echo '</div>';
    echo '</div>';
    return;
}

try {
    $actor_data = ModPlaybillActorHelper::getActorData($actor_id, $api_base_url, $public_base_url);
} catch (Exception $e) {
    echo '<div class="playbill-error" style="padding: 10px; background: #fee; border: 1px solid #fcc; color: #c00; border-radius: 4px; margin: 10px 0;">';
    echo 'Playbill Actor Module: Error loading data for Actor ID ' . htmlspecialchars($actor_id) . ': ' . htmlspecialchars($e->getMessage());
    if (Factory::getApplication()->get('debug')) {
        echo '<br>API URL: ' . htmlspecialchars($api_base_url . '/actor/' . $actor_id);
    }
    echo '</div>';
    echo '</div>';
    return;
}

if (!$actor_data) {
    echo '<div class="playbill-error" style="padding: 15px; background: #fee; border: 2px solid #fcc; color: #c00; border-radius: 4px; margin: 10px 0;">';
    echo '<strong>Playbill Actor Module Error</strong><br>';
    echo 'Actor not found or error loading data for Actor ID: <strong>' . htmlspecialchars($actor_id) . '</strong><br>';
    echo 'Please verify:<br>';
    echo '1. The Actor ID is correct in the database<br>';
    echo '2. The API endpoint is accessible: <code>' . htmlspecialchars($api_base_url . '/actor/' . $actor_id) . '</code><br>';
    echo '3. Check Joomla error logs for detailed error messages<br>';
    if (Factory::getApplication()->get('debug')) {
        echo '<br><strong>Debug Info:</strong><br>';
        echo 'API Base URL: ' . htmlspecialchars($api_base_url) . '<br>';
        echo 'Full API URL: ' . htmlspecialchars($api_base_url . '/actor/' . $actor_id) . '<br>';
    }
    echo '</div>';
    echo '</div>';
    return;
}

if (empty($actor_data['credits']) || !is_array($actor_data['credits'])) {
    echo '<div class="playbill-actor-module" style="margin: 20px 0; padding: 20px; border: 1px solid #e5e7eb; border-radius: 8px; background: #fff;">';
    echo '<h2 class="playbill-title" style="font-size: 28px; font-weight: bold; margin-bottom: 15px; color: #1f2937;">';
    echo htmlspecialchars($actor_data['name'] ?? 'Unknown Actor');
    echo '</h2>';
    echo '<p style="color: #6b7280; padding: 20px; text-align: center;">No credits found for this actor.</p>';
    echo '</div>';
    echo '</div>';
    return;
}

try {
    $credits_by_category = ModPlaybillActorHelper::groupCreditsByCategory($actor_data['credits']);
    
    $all_credits = [];
    if (!empty($actor_data['credits']) && is_array($actor_data['credits'])) {
        $all_credits = $actor_data['credits'];
        usort($all_credits, function($a, $b) {
            $nameA = isset($a['person']['name']) ? strtolower($a['person']['name']) : (isset($a['show']['title']) ? strtolower($a['show']['title']) : '');
            $nameB = isset($b['person']['name']) ? strtolower($b['person']['name']) : (isset($b['show']['title']) ? strtolower($b['show']['title']) : '');
            return strcmp($nameA, $nameB);
        });
    }
} catch (Exception $e) {
    echo '<div class="playbill-actor-module" style="margin: 20px 0; padding: 20px; border: 1px solid #e5e7eb; border-radius: 8px; background: #fff;">';
    echo '<h2 class="playbill-title" style="font-size: 28px; font-weight: bold; margin-bottom: 15px; color: #1f2937;">';
    echo htmlspecialchars($actor_data['name'] ?? 'Unknown Actor');
    echo '</h2>';
    echo '<div class="playbill-error" style="padding: 10px; background: #fee; border: 1px solid #fcc; color: #c00; border-radius: 4px; margin: 10px 0;">';
    echo 'Playbill Actor Module: Error processing credits: ' . htmlspecialchars($e->getMessage());
    echo '</div>';
    echo '</div>';
    echo '</div>';
    return;
}

?>
<div class="playbill-actor-module" style="margin: 20px 0;">
    <div style="background: white; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border-radius: 8px; overflow: hidden; margin-bottom: 24px;">
        <div style="padding: 20px 24px; background: linear-gradient(to right, #1e1e1e, #373737);">
            <div style="display: flex; align-items: center; gap: 24px;">
                <div style="flex-shrink: 0; position: relative;">
                    <?php if (!empty($actor_data['photo'])): ?>
                    <img src="<?php echo htmlspecialchars($actor_data['photo']); ?>" 
                         alt="<?php echo htmlspecialchars($actor_data['name']); ?>" 
                         style="width: 192px; height: 288px; object-fit: cover; border-radius: 8px; border: 4px solid white; box-shadow: 0 10px 15px rgba(0,0,0,0.2);">
                    <?php else: ?>
                    <div style="width: 192px; height: 288px; background: #d1d5db; border-radius: 8px; border: 4px solid white; box-shadow: 0 10px 15px rgba(0,0,0,0.2); display: flex; align-items: center; justify-content: center;">
                        <span style="color: #6b7280; font-size: 12px; text-align: center; padding: 8px;">No Photo</span>
                    </div>
                    <?php endif; ?>
                </div>
                <div style="flex: 1; display: flex; flex-direction: row; align-items: center; justify-content: space-between;">
                    <div>
                        <h1 style="font-size: 30px; font-weight: bold; color: white; margin: 0;">
                            <?php echo htmlspecialchars($actor_data['name']); ?>
                        </h1>
                    </div>
                    <div style="margin-right: 180px;">
                        <div style="display: flex; flex-direction: column; gap: 16px;">
                            <div>
                                <span style="display: block; font-size: 14px; color: rgba(255,255,255,0.8); margin-bottom: 4px;">Total Credits</span>
                                <p style="font-size: 24px; font-weight: bold; color: white; margin: 0;">
                                    <?php echo isset($actor_data['total_credits']) ? (int)$actor_data['total_credits'] : count($actor_data['credits'] ?? []); ?>
                                </p>
                            </div>
                            <?php 
                            $roles_list = isset($actor_data['roles']) && is_array($actor_data['roles']) ? $actor_data['roles'] : [];
                            
                            if (empty($roles_list) && !empty($actor_data['credits']) && is_array($actor_data['credits'])) {
                                $roles_set = [];
                                foreach ($actor_data['credits'] as $credit) {
                                    if (isset($credit['role']) && !empty($credit['role']) && is_string($credit['role'])) {
                                        $role_trimmed = trim($credit['role']);
                                        if (!empty($role_trimmed)) {
                                            $roles_set[$role_trimmed] = true;
                                        }
                                    }
                                }
                                $roles_list = array_keys($roles_set);
                                sort($roles_list);
                            }
                            
                            $roles_count = count($roles_list);
                            
                            if (!empty($roles_list) && $roles_count > 0): ?>
                            <div>
                                <span style="display: block; font-size: 14px; color: rgba(255,255,255,0.8); margin-bottom: 4px;">Positions</span>
                                <p style="font-size: 24px; font-weight: bold; color: white; margin: 0 0 4px 0;">
                                    <?php echo $roles_count; ?>
                                </p>
                                <p style="font-size: 14px; color: rgba(255,255,255,0.9); margin: 0; line-height: 1.4;">
                                    <?php 
                                    $roles_display = array_map('trim', $roles_list);
                                    $roles_display = array_filter($roles_display);
                                    echo htmlspecialchars(implode(', ', $roles_display)); 
                                    ?>
                                </p>
                            </div>
                            <?php elseif (!empty($actor_data['disciplines'])): ?>
                            <div>
                                <span style="display: block; font-size: 14px; color: rgba(255,255,255,0.8); margin-bottom: 4px;">Disciplines</span>
                                <p style="font-size: 24px; font-weight: bold; color: white; margin: 0 0 4px 0;">
                                    <?php 
                                        if (isset($actor_data['disciplines_count'])) {
                                            echo (int)$actor_data['disciplines_count'];
                                        } else {
                                            $disciplines_array = explode(',', $actor_data['disciplines']);
                                            echo count(array_filter(array_map('trim', $disciplines_array)));
                                        }
                                    ?>
                                </p>
                                <p style="font-size: 14px; color: rgba(255,255,255,0.9); margin: 0;">
                                    <?php echo htmlspecialchars($actor_data['disciplines']); ?>
                                </p>
                            </div>
                            <?php endif; ?>
                            <?php if (!empty($actor_data['theaters']) && is_array($actor_data['theaters'])): ?>
                            <div>
                                <span style="display: block; font-size: 14px; color: rgba(255,255,255,0.8); margin-bottom: 4px;">Theaters</span>
                                <p style="font-size: 24px; font-weight: bold; color: white; margin: 0 0 4px 0;">
                                    <?php echo count($actor_data['theaters']); ?>
                                </p>
                                <?php if (count($actor_data['theaters']) > 0): ?>
                                <p style="font-size: 14px; color: rgba(255,255,255,0.9); margin: 0;">
                                    <?php 
                                        $theater_names = array_map(function($t) { return isset($t['name']) ? $t['name'] : ''; }, array_filter($actor_data['theaters'], function($t) { return isset($t['name']); }));
                                        echo htmlspecialchars(implode(', ', $theater_names)); 
                                    ?>
                                </p>
                                <?php endif; ?>
                            </div>
                            <?php endif; ?>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <div style="display: flex; flex-direction: column; gap: 24px;">
        <?php if (!empty($actor_data['credits']) && is_array($actor_data['credits'])): ?>
        <div class="playbill-actor-grid">
            <div style="background: white; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border-radius: 8px; overflow: hidden;">
                <div style="padding: 16px 24px; border-bottom: 1px solid #e5e7eb;">
                    <h2 style="font-size: 20px; font-weight: 600; color: #111827; margin: 0; display: inline-block; margin-right: 20px;">Credits</h2>
                    <div style="display: inline-block;">
                        <button onclick="showCreditsView('category')" id="credits-category-btn" style="padding: 6px 16px; margin-right: 8px; background: #4f46e5; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: 600; font-size: 13px;">By Category</button>
                        <button onclick="showCreditsView('alphabetical')" id="credits-alphabetical-btn" style="padding: 6px 16px; background: #e5e7eb; color: #6b7280; border: none; border-radius: 4px; cursor: pointer; font-weight: 600; font-size: 13px;">Alphabetical</button>
                    </div>
                </div>
                <div style="padding: 24px;">
                <div id="credits-category-view">
                <?php if (!empty($credits_by_category)): ?>
                <?php foreach ($credits_by_category as $category => $credits): ?>
                <?php 
                    try {
                        if (!is_array($credits) || empty($credits)) {
                            continue;
                        }
                ?>
                <div style="margin-bottom: 32px;">
                    <h3 style="font-size: 18px; font-weight: 600; color: #1f2937; margin-bottom: 16px; padding-bottom: 8px; border-bottom: 1px solid #e5e7eb;">
                        <?php echo htmlspecialchars($category); ?>
                    </h3>
                    <div style="display: flex; flex-direction: column; gap: 16px;">
                        <?php foreach ($credits as $credit): ?>
                        <?php 
                            if (!isset($credit) || !is_array($credit)) {
                                continue;
                            }
                            $show = isset($credit['show']) && is_array($credit['show']) ? $credit['show'] : null;
                            $theater = isset($credit['theater']) && is_array($credit['theater']) ? $credit['theater'] : null;
                            if (!$show && !$theater) {
                                continue;
                            }
                        ?>
                        <div style="display: flex; align-items: flex-start; justify-content: space-between; padding: 16px; background: #f9fafb; border-radius: 8px; transition: background 0.2s;" 
                             onmouseover="this.style.background='#f3f4f6'"
                             onmouseout="this.style.background='#f9fafb'">
                            <div style="flex: 1;">
                                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
                                    <?php if ($show && isset($show['id']) && isset($show['title'])): ?>
                                    <?php
                                    $show_url = '';
                                    if (strpos($show_profile_url, 'index.php') !== false) {
                                        if (strpos($show_profile_url, '?') !== false) {
                                            $show_url = $show_profile_url . '&id=' . (int)$show['id'] . '&type=show';
                                        } else {
                                            $show_url = $show_profile_url . '?id=' . (int)$show['id'] . '&type=show';
                                        }
                                    } else {
                                        $show_url = rtrim($show_profile_url, '/') . '/show/' . (int)$show['id'];
                                    }
                                    ?>
                                    <a href="<?php echo htmlspecialchars($show_url); ?>" 
                                       style="font-weight: 600; color: #4f46e5; text-decoration: none; font-size: 16px;"
                                       onmouseover="this.style.color='#4338ca'"
                                       onmouseout="this.style.color='#4f46e5'">
                                        <?php echo htmlspecialchars($show['title']); ?>
                                    </a>
                                    <?php elseif ($show && isset($show['title'])): ?>
                                    <span style="font-weight: 600; color: #1f2937; font-size: 16px;"><?php echo htmlspecialchars($show['title']); ?></span>
                                    <?php else: ?>
                                    <span style="font-weight: 600; color: #1f2937; font-size: 16px;">Unknown Show</span>
                                    <?php endif; ?>
                                    <?php if (!empty($credit['is_equity'])): ?>
                                    <span style="display: inline-flex; align-items: center; padding: 2px 8px; border-radius: 9999px; font-size: 12px; font-weight: 500; background: #d1fae5; color: #065f46;">
                                        Equity
                                    </span>
                                    <?php endif; ?>
                                </div>
                                <p style="color: #4b5563; margin: 0; font-size: 14px;">
                                    <span style="font-weight: 500;"><?php echo !empty($credit['role']) && is_string($credit['role']) ? htmlspecialchars($credit['role']) : htmlspecialchars($category); ?></span>
                                    <span style="margin: 0 8px;">•</span>
                                    <?php if ($theater && isset($theater['id']) && isset($theater['name'])): ?>
                                    <?php
                                    $theater_url = '';
                                    if (strpos($theater_profile_url, 'index.php') !== false) {
                                        if (strpos($theater_profile_url, '?') !== false) {
                                            $theater_url = $theater_profile_url . '&id=' . (int)$theater['id'] . '&type=theater';
                                        } else {
                                            $theater_url = $theater_profile_url . '?id=' . (int)$theater['id'] . '&type=theater';
                                        }
                                    } else {
                                        $theater_url = rtrim($theater_profile_url, '/') . '/theater/' . (int)$theater['id'];
                                    }
                                    ?>
                                    <a href="<?php echo htmlspecialchars($theater_url); ?>" 
                                       style="color: #4f46e5; text-decoration: none;"
                                       onmouseover="this.style.textDecoration='underline'"
                                       onmouseout="this.style.textDecoration='none'">
                                        <?php echo htmlspecialchars($theater['name']); ?>
                                    </a>
                                    <?php else: ?>
                                    <span><?php echo ($theater && isset($theater['name'])) ? htmlspecialchars($theater['name']) : 'Unknown Theater'; ?></span>
                                    <?php endif; ?>
                                    <?php if (isset($credit['year']) && $credit['year']): ?>
                                    <span style="margin: 0 8px;">•</span>
                                    <span style="color: #6b7280;"><?php echo (int)$credit['year']; ?></span>
                                    <?php endif; ?>
                                </p>
                            </div>
                        </div>
                        <?php endforeach; ?>
                    </div>
                </div>
                <?php 
                    } catch (Throwable $e) {
                        echo '<div class="playbill-error" style="padding: 10px; background: #fee; border: 1px solid #fcc; color: #c00; border-radius: 4px; margin: 10px 0;">';
                        echo 'Error displaying category "' . htmlspecialchars($category) . '": ' . htmlspecialchars($e->getMessage());
                        if (Factory::getApplication()->get('debug')) {
                            echo '<br>File: ' . htmlspecialchars($e->getFile()) . ' Line: ' . $e->getLine();
                        }
                        echo '</div>';
                    }
                ?>
                <?php endforeach; ?>
                <?php endif; ?>
                </div>
                
                <div id="credits-alphabetical-view" style="display: none;">
                <?php if (!empty($all_credits)): ?>
                <div style="display: flex; flex-direction: column; gap: 16px;">
                    <?php foreach ($all_credits as $credit): ?>
                    <?php 
                        if (!isset($credit) || !is_array($credit)) {
                            continue;
                        }
                        $show = isset($credit['show']) && is_array($credit['show']) ? $credit['show'] : null;
                        $theater = isset($credit['theater']) && is_array($credit['theater']) ? $credit['theater'] : null;
                        if (!$show && !$theater) {
                            continue;
                        }
                    ?>
                    <div style="display: flex; align-items: flex-start; justify-content: space-between; padding: 16px; background: #f9fafb; border-radius: 8px; transition: background 0.2s;" 
                         onmouseover="this.style.background='#f3f4f6'"
                         onmouseout="this.style.background='#f9fafb'">
                        <div style="flex: 1;">
                            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
                                <?php if ($show && isset($show['id']) && isset($show['title'])): ?>
                                <?php
                                $show_url = '';
                                if (strpos($show_profile_url, 'index.php') !== false) {
                                    if (strpos($show_profile_url, '?') !== false) {
                                        $show_url = $show_profile_url . '&id=' . (int)$show['id'] . '&type=show';
                                    } else {
                                        $show_url = $show_profile_url . '?id=' . (int)$show['id'] . '&type=show';
                                    }
                                } else {
                                    $show_url = rtrim($show_profile_url, '/') . '/show/' . (int)$show['id'];
                                }
                                ?>
                                <a href="<?php echo htmlspecialchars($show_url); ?>" 
                                   style="font-weight: 600; color: #4f46e5; text-decoration: none; font-size: 16px;"
                                   onmouseover="this.style.color='#4338ca'"
                                   onmouseout="this.style.color='#4f46e5'">
                                    <?php echo htmlspecialchars($show['title']); ?>
                                </a>
                                <?php elseif ($show && isset($show['title'])): ?>
                                <span style="font-weight: 600; color: #1f2937; font-size: 16px;"><?php echo htmlspecialchars($show['title']); ?></span>
                                <?php else: ?>
                                <span style="font-weight: 600; color: #1f2937; font-size: 16px;">Unknown Show</span>
                                <?php endif; ?>
                                <?php if (!empty($credit['is_equity'])): ?>
                                <span style="display: inline-flex; align-items: center; padding: 2px 8px; border-radius: 9999px; font-size: 12px; font-weight: 500; background: #d1fae5; color: #065f46;">
                                    Equity
                                </span>
                                <?php endif; ?>
                            </div>
                            <p style="color: #4b5563; margin: 0; font-size: 14px;">
                                <span style="font-weight: 500;"><?php echo !empty($credit['role']) && is_string($credit['role']) ? htmlspecialchars($credit['role']) : (isset($credit['category']) ? htmlspecialchars($credit['category']) : ''); ?></span>
                                <?php if (isset($credit['category']) && !empty($credit['category'])): ?>
                                <span style="color: #9ca3af; margin-left: 8px; font-size: 13px;">(<?php echo htmlspecialchars($credit['category']); ?>)</span>
                                <?php endif; ?>
                                <span style="margin: 0 8px;">•</span>
                                <?php if ($theater && isset($theater['id']) && isset($theater['name'])): ?>
                                <?php
                                $theater_url = '';
                                if (strpos($theater_profile_url, 'index.php') !== false) {
                                    if (strpos($theater_profile_url, '?') !== false) {
                                        $theater_url = $theater_profile_url . '&id=' . (int)$theater['id'] . '&type=theater';
                                    } else {
                                        $theater_url = $theater_profile_url . '?id=' . (int)$theater['id'] . '&type=theater';
                                    }
                                } else {
                                    $theater_url = rtrim($theater_profile_url, '/') . '/theater/' . (int)$theater['id'];
                                }
                                ?>
                                <a href="<?php echo htmlspecialchars($theater_url); ?>" 
                                   style="color: #4f46e5; text-decoration: none;"
                                   onmouseover="this.style.textDecoration='underline'"
                                   onmouseout="this.style.textDecoration='none'">
                                    <?php echo htmlspecialchars($theater['name']); ?>
                                </a>
                                <?php else: ?>
                                <span><?php echo ($theater && isset($theater['name'])) ? htmlspecialchars($theater['name']) : 'Unknown Theater'; ?></span>
                                <?php endif; ?>
                                <?php if (isset($credit['year']) && $credit['year']): ?>
                                <span style="margin: 0 8px;">•</span>
                                <span style="color: #6b7280;"><?php echo (int)$credit['year']; ?></span>
                                <?php endif; ?>
                            </p>
                        </div>
                    </div>
                    <?php endforeach; ?>
                </div>
                <?php else: ?>
                <p style="color: #6b7280; padding: 20px; text-align: center;">No credits found for this actor.</p>
                <?php endif; ?>
                </div>
                </div>
            </div>
        </div>
        <?php endif; ?>
    </div>
    
    <?php if (!empty($actor_data['theaters']) && is_array($actor_data['theaters']) && count($actor_data['theaters']) > 0): ?>
    <div style="margin-top: 24px;">
        <div class="playbill-theaters-grid">
            <div style="background: white; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border-radius: 8px; overflow: hidden;">
                <div style="padding: 16px 24px; border-bottom: 1px solid #e5e7eb;">
                    <h2 style="font-size: 18px; font-weight: 600; color: #111827; margin: 0;">Theaters</h2>
                </div>
                <div style="padding: 24px;">
                    <div style="display: flex; flex-direction: column; gap: 8px;">
                        <?php foreach ($actor_data['theaters'] as $theater): ?>
                        <?php if (isset($theater['id']) && isset($theater['name'])): ?>
                        <?php
                        $theater_url = '';
                        if (strpos($theater_profile_url, 'index.php') !== false) {
                            if (strpos($theater_profile_url, '?') !== false) {
                                $theater_url = $theater_profile_url . '&id=' . (int)$theater['id'] . '&type=theater';
                            } else {
                                $theater_url = $theater_profile_url . '?id=' . (int)$theater['id'] . '&type=theater';
                            }
                        } else {
                            $theater_url = rtrim($theater_profile_url, '/') . '/theater/' . (int)$theater['id'];
                        }
                        ?>
                        <a href="<?php echo htmlspecialchars($theater_url); ?>" 
                           style="display: block; color: #4f46e5; text-decoration: none; font-size: 14px; padding: 4px 0;"
                           onmouseover="this.style.textDecoration='underline'"
                           onmouseout="this.style.textDecoration='none'">
                            <?php echo htmlspecialchars($theater['name']); ?>
                        </a>
                        <?php endif; ?>
                        <?php endforeach; ?>
                    </div>
                </div>
            </div>
            
            <?php if (!empty($actor_data['theaters_map']) && is_array($actor_data['theaters_map']) && count($actor_data['theaters_map']) > 0): ?>
            <div style="background: white; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border-radius: 8px; overflow: hidden;">
                <div style="padding: 16px 24px; border-bottom: 1px solid #e5e7eb;">
                    <h2 style="font-size: 18px; font-weight: 600; color: #111827; margin: 0;">Theater Locations</h2>
                </div>
                <div style="padding: 24px;">
                    <div id="actor-map" style="height: 400px; width: 100%; border-radius: 8px;"></div>
                </div>
            </div>
            <?php endif; ?>
        </div>
    </div>
    <?php endif; ?>
    
    <?php if (empty($actor_data['credits']) || !is_array($actor_data['credits'])): ?>
    <div style="background: white; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border-radius: 8px; overflow: hidden; padding: 24px; text-align: center;">
        <p style="color: #6b7280; margin: 0;">No credits found for this actor.</p>
    </div>
    <?php endif; ?>
</div>
<!-- Playbill Actor Module END -->
<?php
} catch (Throwable $e) {
    echo '<div class="playbill-error" style="padding: 10px; background: #fee; border: 1px solid #fcc; color: #c00; border-radius: 4px; margin: 10px 0;">';
    echo 'Playbill Actor Module: Fatal error: ' . htmlspecialchars($e->getMessage());
    echo '<br>File: ' . htmlspecialchars($e->getFile()) . ' Line: ' . $e->getLine();
    echo '</div>';
}
?>
<?php if (isset($actor_data) && !empty($actor_data['theaters_map']) && is_array($actor_data['theaters_map']) && count($actor_data['theaters_map']) > 0): ?>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
(function() {
    const theaters = <?php echo json_encode($actor_data['theaters_map']); ?>;
    const publicBaseUrl = <?php echo json_encode($public_base_url); ?>;
    
    if (theaters && theaters.length > 0) {
        const map = L.map('actor-map').setView([39.8283, -98.5795], 4);
        
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);
        
        const bounds = [];
        
        theaters.forEach(function(theater) {
            if (theater.lat && theater.lng) {
                const marker = L.marker([theater.lat, theater.lng]).addTo(map);
                let popupContent = '<div style="padding: 8px;">';
                popupContent += '<strong><a href="' + publicBaseUrl + '/theater/' + theater.id + '" style="color: #4f46e5; text-decoration: none;">' + (theater.name || 'Theater') + '</a></strong>';
                if (theater.city || theater.state) {
                    popupContent += '<br><span style="color: #6b7280;">' + (theater.city || '') + (theater.city && theater.state ? ', ' : '') + (theater.state || '') + '</span>';
                }
                popupContent += '</div>';
                marker.bindPopup(popupContent);
                bounds.push([theater.lat, theater.lng]);
            }
        });
        
        if (bounds.length > 0) {
            map.fitBounds(bounds, { padding: [20, 20] });
        }
    }
})();
</script>
<?php endif; ?>
<script>
function showCreditsView(view) {
    const categoryView = document.getElementById('credits-category-view');
    const alphabeticalView = document.getElementById('credits-alphabetical-view');
    const categoryBtn = document.getElementById('credits-category-btn');
    const alphabeticalBtn = document.getElementById('credits-alphabetical-btn');
    
    if (view === 'category') {
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
<style>
#playbill-actor-module-container ~ .item-page,
#playbill-actor-module-container ~ article,
#playbill-actor-module-container ~ .item-page,
#playbill-actor-module-container ~ article {
    display: none !important;
}
body.item-view .item-page:has(+ #playbill-actor-module-container),
body.item-view article:has(+ #playbill-actor-module-container) {
    display: none !important;
}
</style>
<script>
(function() {
    document.addEventListener('DOMContentLoaded', function() {
        const moduleContainer = document.getElementById('playbill-actor-module-container');
        if (moduleContainer) {
            const articleContent = moduleContainer.closest('.item-page') || 
                                 moduleContainer.closest('article') ||
                                 document.querySelector('.item-page') ||
                                 document.querySelector('article');
            if (articleContent && articleContent !== moduleContainer && !articleContent.contains(moduleContainer)) {
                articleContent.style.display = 'none';
            }
            
            const nextSibling = moduleContainer.nextElementSibling;
            if (nextSibling && (nextSibling.classList.contains('item-page') || nextSibling.tagName === 'ARTICLE')) {
                nextSibling.style.display = 'none';
            }
            
            const parent = moduleContainer.parentElement;
            if (parent) {
                const siblings = Array.from(parent.children);
                const moduleIndex = siblings.indexOf(moduleContainer);
                siblings.slice(moduleIndex + 1).forEach(function(sibling) {
                    if (sibling.classList.contains('item-page') || 
                        sibling.classList.contains('article-content') ||
                        sibling.tagName === 'ARTICLE' ||
                        (sibling.classList.contains('content') && !sibling.contains(moduleContainer))) {
                        sibling.style.display = 'none';
                    }
                });
            }
        }
    });
})();
</script>
</div>

