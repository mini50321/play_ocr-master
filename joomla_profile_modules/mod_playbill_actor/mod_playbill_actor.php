<?php
defined('_JEXEC') or die;

use Joomla\CMS\Helper\ModuleHelper;
use Joomla\CMS\Factory;

require_once __DIR__ . '/helper/mod_playbill_actor.php';
require ModuleHelper::getLayoutPath('mod_playbill_actor', $params->get('layout', 'default'));

