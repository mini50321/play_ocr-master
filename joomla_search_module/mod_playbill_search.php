<?php
defined('_JEXEC') or die;

use Joomla\CMS\Helper\ModuleHelper;

require_once __DIR__ . '/helper/mod_playbill_search.php';
require ModuleHelper::getLayoutPath('mod_playbill_search', $params->get('layout', 'default'));

