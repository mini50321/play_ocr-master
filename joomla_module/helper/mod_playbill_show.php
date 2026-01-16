<?php
defined('_JEXEC') or die;

use Joomla\CMS\Log\Log;

class ModPlaybillShowHelper
{
    public static function getProductionData($show_id, $api_base_url, $public_base_url)
    {
        if (empty($show_id)) {
            return null;
        }
        
        $url = $api_base_url . '/show/' . urlencode($show_id);
        $ch = curl_init($url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_TIMEOUT, 10);
        curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
        $response = curl_exec($ch);
        $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        
        if ($http_code !== 200) {
            Log::add('Playbill module error: HTTP ' . $http_code . ' for show ID ' . $show_id, Log::ERROR, 'mod_playbill_show');
            return null;
        }
        
        $data = json_decode($response, true);
        
        if (!$data || isset($data['error'])) {
            return null;
        }
        
        if (isset($data['productions']) && !empty($data['productions'])) {
            $production = $data['productions'][0];
            $production['show'] = [
                'id' => $data['id'],
                'title' => $data['title']
            ];
            $production['public_base_url'] = $public_base_url;
            return $production;
        }
        
        return null;
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

