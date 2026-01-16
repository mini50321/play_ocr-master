<?php
defined('_JEXEC') or die;

use Joomla\CMS\Log\Log;
use Joomla\CMS\Factory;

class ModPlaybillTheaterHelper
{
    public static function getTheaterData($theater_id, $api_base_url, $public_base_url)
    {
        if (empty($theater_id)) {
            return null;
        }
        
        $url = $api_base_url . '/theater/' . urlencode($theater_id);
        $ch = curl_init($url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_TIMEOUT, 10);
        curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
        $response = curl_exec($ch);
        $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        
        if ($http_code !== 200) {
            Log::add('Playbill theater module error: HTTP ' . $http_code . ' for theater ID ' . $theater_id, Log::ERROR, 'mod_playbill_theater');
            return null;
        }
        
        $data = json_decode($response, true);
        
        if (!$data || isset($data['error'])) {
            return null;
        }
        
        $data['public_base_url'] = $public_base_url;
        return $data;
    }
}

