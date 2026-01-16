<?php
defined('_JEXEC') or die;

use Joomla\CMS\Log\Log;
use Joomla\CMS\Factory;

class ModPlaybillActorHelper
{
    public static function getActorData($actor_id, $api_base_url, $public_base_url)
    {
        if (empty($actor_id)) {
            return null;
        }
        
        $url = $api_base_url . '/actor/' . urlencode($actor_id);
        $ch = curl_init($url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_TIMEOUT, 10);
        curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
        $response = curl_exec($ch);
        $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        
        if ($http_code !== 200) {
            Log::add('Playbill actor module error: HTTP ' . $http_code . ' for actor ID ' . $actor_id, Log::ERROR, 'mod_playbill_actor');
            return null;
        }
        
        $data = json_decode($response, true);
        
        if (!$data || isset($data['error'])) {
            return null;
        }
        
        $data['public_base_url'] = $public_base_url;
        return $data;
    }
    
    public static function groupCreditsByCategory($credits)
    {
        $grouped = [];
        foreach ($credits as $credit) {
            $category = $credit['category'];
            if (!isset($grouped[$category])) {
                $grouped[$category] = [];
            }
            $grouped[$category][] = $credit;
        }
        return $grouped;
    }
}

