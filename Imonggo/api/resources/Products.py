from Imonggo.api.lib.mapping import Mapping
from Imonggo.api.lib.filters import FilterSet, StringFilter, NumberFilter, DateFilter, BoolFilter
from . import ResourceObject


class Products(ResourceObject):
    resource_name = "product"
    
    @classmethod
    def filter_set(cls):
        fs = FilterSet(before = DateFilter(),
                         after = DateFilter(),
                         to = DateFilter(), 
                         branch_id = NumberFilter(),
                         ) 
        fs["from"] = DateFilter()
        return fs