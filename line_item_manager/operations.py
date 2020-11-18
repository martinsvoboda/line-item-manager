from .config import config
from .gam_operations import GAMOperations

log = config.getLogger('operations')

class AppOperations(GAMOperations):
    @property
    def client(self):
        return config.client

    @property
    def version(self):
        return config.app['googleads']['version']

    @property
    def dry_run(self):
        return config.cli['dry_run']

class AdUnit(AppOperations):
    service = 'InventoryService'
    method = 'getAdUnitsByStatement'

class Advertiser(AppOperations):
    service = 'CompanyService'
    method = 'getCompaniesByStatement'
    create_method = 'createCompanies'

    def __init__(self, *args, _type='ADVERTISER', **kwargs):
        self.create_dry_run = [dict(id=f"{kwargs['name']}-0")]
        kwargs['type'] = _type
        super().__init__(*args, **kwargs)

class CurrentNetwork(AppOperations):
    service = 'NetworkService'
    method = 'getCurrentNetwork'

class CurrentUser(AppOperations):
    service = 'UserService'
    method = 'getCurrentUser'

class Placement(AppOperations):
    service = 'PlacementService'
    method = 'getPlacementsByStatement'

class TargetingKey(AppOperations):
    service = 'CustomTargetingService'
    method = 'getCustomTargetingKeysByStatement'
    create_method = 'createCustomTargetingKeys'

    def __init__(self, *args, name=None, _type='PREDEFINED', **kwargs):
        self.create_dry_run = [dict(id=f"{name}-0")]
        kwargs['name'] = name
        kwargs['displayName'] = kwargs.get('displayName', name)
        kwargs['type'] = _type
        super().__init__(*args, **kwargs)

class LineItem(AppOperations):
    service = 'LineItemService'
    method = 'getLineItemsByStatement'
    create_method = 'createLineItems'

    def create(self, recs=None):
        if self.dry_run:
            _ = [rec.update({'id': f"{rec['name']}-{_i}"}) for _i, rec in enumerate(recs)]
            self.create_dry_run = recs
        results = super().create(recs)
        names = {_r['name'] for _r in recs}
        cur_names = {_r['name'] for _r in results}
        missing = [_n for _n in names if _n not in cur_names]
        if missing:
            raise ValueError(f'Following names were not found after creation: \'{missing}\'')
        return results

class TargetingValues(AppOperations):
    service = 'CustomTargetingService'
    method = 'getCustomTargetingValuesByStatement'
    create_method = 'createCustomTargetingValues'

    def __init__(self, *args, key_id=None, **kwargs):
        kwargs['customTargetingKeyId'] = key_id
        super().__init__(*args, **kwargs)

    def values(self, name, matchType='EXACT'):
        return dict(
            customTargetingKeyId=self.params['customTargetingKeyId'],
            name=name,
            displayName=name,
            matchType=matchType
        )

    def create(self, names=None):
        results = self.fetch()
        cur_names = {_r['name'] for _r in results}
        recs = [self.values(_n) for _n in names if _n not in cur_names]
        if recs:
            if self.dry_run:
                _ = [rec.update({'id': f"{rec['name']}-{_i}"}) for _i, rec in enumerate(recs)]
                self.create_dry_run = recs
            results += super().create(recs)
        cur_names = {_r['name'] for _r in results}
        missing = [_n for _n in names if _n not in cur_names]
        if missing:
            raise ValueError(f'Following names were not found after creation: \'{missing}\'')
        return results

class Order(AppOperations):
    service = "OrderService"
    method = 'getOrdersByStatement'
    create_method = 'createOrders'

    def __init__(self, *args, **kwargs):
        self.create_dry_run = [dict(id=f"{kwargs['name']}-0")]
        super().__init__(*args, **kwargs)

class Creative(AppOperations):
    service = "CreativeService"
    method = 'getCreativesByStatement'
    create_method = 'createCreatives'
    query_fields = ('id', 'name', 'advertiserId', 'width', 'height')

    def __init__(self, *args, **kwargs):
        if 'size' in kwargs:
            kwargs['height'] = kwargs['size']['height']
            kwargs['width'] = kwargs['size']['width']
        super().__init__(*args, **kwargs)

class CreativeVideo(Creative):
    create_fields = ('xsi_type', 'name', 'advertiserId', 'size', 'vastXmlUrl', 'vastRedirectType', 'duration')

    def __init__(self, *args, xsi_type='VastRedirectCreative', vastRedirectType='LINEAR', duration=60, **kwargs):
        kwargs['xsi_type'] = xsi_type
        kwargs['vastRedirectType'] = vastRedirectType
        kwargs['duration'] = duration
        super().__init__(*args, **kwargs)

class CreativeBanner(Creative):
    create_fields = ('xsi_type', 'name', 'advertiserId', 'size', 'isSafeFrameCompatible', 'snippet')

    def __init__(self, *args, xsi_type='ThirdPartyCreative', isSafeFrameCompatible=True, **kwargs):
        kwargs['xsi_type'] = xsi_type
        kwargs['isSafeFrameCompatible'] = isSafeFrameCompatible
        super().__init__(*args, **kwargs)