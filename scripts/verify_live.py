import urllib.request
import json

BASE = 'http://127.0.0.1:8000'

def post(path, data, token=None):
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(data).encode('utf-8'),
        headers={'Content-Type': 'application/json', **({'Authorization': f'Bearer {token}'} if token else {})}
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))

def get(path, token=None):
    req = urllib.request.Request(
        BASE + path,
        headers={'Authorization': f'Bearer {token}'} if token else {}
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))

def delete(path, token=None):
    req = urllib.request.Request(
        BASE + path,
        headers={'Authorization': f'Bearer {token}'} if token else {},
        method='DELETE'
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))

# 1. Login or register
try:
    auth_data = post('/api/auth/register', {
        'email': 'tester_audit_live@foodfresh.local',
        'password': 'Password123!',
        'fullName': 'Live Audit Tester',
        'householdType': 'Couple'
    })
except Exception:
    auth_data = post('/api/auth/login', {
        'email': 'tester_audit_live@foodfresh.local',
        'password': 'Password123!'
    })

token = auth_data['token']
print('Authenticated token:', token[:15] + '...')

# 2. Add item to pantry
item = {
    'foodName': 'Nagpur Oranges',
    'cultivar': 'Nagpur Sweet Mandarin',
    'qualityScore': 90,
    'qualityPeriod': '12 days remaining',
    'remainingDays': 12,
    'storageEnvironment': 'Pantry Basket',
    'guidance': 'Store in cool ventilated space.'
}
add_resp = post('/api/history', {'item': item}, token)
item_id = add_resp['item']['id']
print('Added item successfully:', item_id, add_resp['item']['foodName'])

# 3. Verify GET /api/history returns active item + count
hist = get('/api/history', token)
assert any(i['id'] == item_id for i in hist['items']), 'Item should be in active pantry'
print('Active items in pantry:', hist['count'])
print('Archived items in pantry:', hist['archived_count'])
print('Total activity logs:', hist['activity_count'])

# 4. Remove / Consume item via POST /api/analytics/action
act_resp = post('/api/analytics/action', {
    'food_name': 'Nagpur Oranges',
    'action': 'consumed',
    'pantry_item_id': item_id,
    'cultivar': 'Nagpur Sweet Mandarin',
    'reason': 'Fresh morning juice'
}, token)
print('Action recorded:', act_resp['message'])

# 5. Verify GET /api/history again: item is NOT in active, but IS in archived_items!
hist2 = get('/api/history', token)
assert not any(i['id'] == item_id for i in hist2['items']), 'Consumed item must NOT be in active pantry!'
assert any(i['id'] == item_id for i in hist2['archived_items']), 'Consumed item MUST be in archived_items!'
archived_item = next(i for i in hist2['archived_items'] if i['id'] == item_id)
print('Archived item retrieved successfully!')
print(' - Food:', archived_item['foodName'])
print(' - Status:', archived_item['removalAction'])
print(' - Reason:', archived_item['removalReason'])
print(' - Archived At:', archived_item['archivedAt'])

# 6. Verify GET /api/analytics
analytics = get('/api/analytics', token)
print('Analytics retrieved successfully!')
print(' - has_activity:', analytics['has_activity'])
print(' - total_consumed:', analytics['total_consumed'])
print(' - total_wasted:', analytics['total_wasted'])
print(' - waste_percentage:', analytics['waste_percentage'])
print(' - food_saved_count:', analytics['food_saved_count'])
print(' - top_consumed_foods:', analytics['top_consumed_foods'])

# 7. Verify GET /api/history/activity-logs
act_logs = get('/api/history/activity-logs', token)
print('Activity logs retrieved successfully! Count:', len(act_logs['logs']))
recent_events = [f"{e['actionType']}: {e['foodName']}" for e in act_logs['logs'][:5]]
print('Recent events:', recent_events)

# 8. Test Restore back to active pantry
restore_resp = post(f'/api/history/{item_id}/restore', {}, token)
print('Restore response:', restore_resp['message'])
hist3 = get('/api/history', token)
assert any(i['id'] == item_id for i in hist3['items']), 'Item must be back in active pantry after restore!'
print('Restored successfully back to active pantry!')

print('\nALL VERIFICATIONS PASSED 100% SUCCESSFULLY!')

