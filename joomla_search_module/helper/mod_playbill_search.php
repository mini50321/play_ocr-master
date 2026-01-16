<?php
defined('_JEXEC') or die;

use Joomla\CMS\Log\Log;

class ModPlaybillSearchHelper
{
    public static function performSearch($query, $api_base_url, $filter_type = 'all', $equity_filter = 'all')
    {
        if (empty($query)) {
            return [
                'actors' => [],
                'shows' => [],
                'theaters' => []
            ];
        }
        
        $url = $api_base_url . '/search?q=' . urlencode($query);
        if ($filter_type !== 'all') {
            $url .= '&type=' . urlencode($filter_type);
        }
        if ($equity_filter !== 'all') {
            $url .= '&equity=' . urlencode($equity_filter);
        }
        
        $ch = curl_init($url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_TIMEOUT, 10);
        curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
        $response = curl_exec($ch);
        $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        
        if ($http_code !== 200) {
            Log::add('Playbill search module error: HTTP ' . $http_code, Log::ERROR, 'mod_playbill_search');
            return [
                'actors' => [],
                'shows' => [],
                'theaters' => []
            ];
        }
        
        $data = json_decode($response, true);
        
        if (!$data || isset($data['error'])) {
            return [
                'actors' => [],
                'shows' => [],
                'theaters' => []
            ];
        }
        
        return $data;
    }
}

