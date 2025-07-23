from collections import defaultdict

from django.core.cache import cache

from apps.rbac.repositories import RoleHierarchyRepository, RoleRepository


class RoleHierarchyManager:
    def __init__(self, cache_key=None):
        self._cache_key = cache_key or "role_hierarchy"
        self._cache_timeout = 3600

    def load(self):
        if cache.get(self._cache_key):
            return cache.get(self._cache_key)

        # 取得所有角色id
        roles = RoleRepository.get_all().values_list("id", flat=True)
        all_roles = set(roles)
        # 取得所有階層關係
        all_edges = RoleHierarchyRepository.get_all_edges()
        tree = defaultdict(list)
        for parent, child in all_edges:
            tree[parent].append(child)
        # 展開所有角色
        result = {}
        for rid in all_roles:
            result[rid] = self._expand(tree, rid)

        cache.set(self._cache_key, result, self._cache_timeout)
        return result

    def reset(self):
        cache.delete(self._cache_key)

    def _expand(self, tree, rid):
        # 回傳包含自己在內的所有子孫id
        result = set([rid])
        for child in tree.get(rid, []):
            result.update(self._expand(tree, child))
        return list(result)
