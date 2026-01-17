<?php
defined('_JEXEC') or die;

use Joomla\CMS\Helper\ModuleHelper;
use Joomla\CMS\Factory;

echo '<!-- MOD_PLAYBILL_ACTOR MODULE FILE LOADED -->';

if (!isset($params)) {
    echo '<div style="padding: 20px; background: #fee; border: 1px solid #fcc; color: #c00;">';
    echo 'ERROR: Module parameters not available.';
    echo '</div>';
    return;
}

require_once __DIR__ . '/helper/mod_playbill_actor.php';

$moduleclass_sfx = htmlspecialchars($params->get('moduleclass_sfx', ''), ENT_COMPAT, 'UTF-8');

require ModuleHelper::getLayoutPath('mod_playbill_actor', $params->get('layout', 'default'));

