from django.shortcuts import render
from django.core.cache import cache
from django.conf import settings
from rest_framework import viewsets
from rest_framework.response import Response

from users.models import User
from users.serializers import UserSerializer


# Create your views here.


def get_cache_key(prefix, identifier=None):
    
    """
    Generate consistent cache keys.
    
    Args:
        prefix: Base name for the cache key (e.g., 'user')
        identifier: Optional identifier to append (e.g., user ID)
    
    Returns:
        String cache key (e.g., 'user_list' or 'user_123')
    
    Examples:
        get_cache_key('user_list') returns 'user_list'
        get_cache_key('user', 5) returns 'user_5'
    """
    if identifier:
        return f"{prefix}_{identifier}"
    return prefix


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint for users with Redis caching.
    
    Implements caching for list and retrieve operations to improve performance.
    Cache is invalidated on create, update, and delete operations.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def list(self, request, *args, **kwargs):
        """
        List all users with caching.
        
        Flow:
        1. Check Redis cache for 'user_list'
        2. If found, return cached data (fast, ~5ms)
        3. If not found, query database (slow, ~50ms)
        4. Save result to cache for 5 minutes
        5. Return data
        
        Cache key: 'user_list'
        TTL: Configured in settings.CACHE_TTL (default 5 minutes)
        """
        # Step 1: Create cache key
        cache_key = get_cache_key('user_list')
        
        # Step 2: Try to get from cache
        cached_data = cache.get(cache_key)
        
        # Step 3: If cache hit, return immediately
        if cached_data is not None:
            print(f"Cache HIT: Returning {len(cached_data)} users from cache")
            return Response(cached_data)
        
        # Step 4: Cache miss - get from database
        print("Cache MISS: Fetching from database...")
        response = super().list(request, *args, **kwargs)
        
        # Step 5: Store in cache
        cache.set(cache_key, response.data, timeout=settings.CACHE_TTL)
        print(f"Cached {len(response.data)} users for {settings.CACHE_TTL} seconds")
        
        # Step 6: Return response
        return response

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a single user with caching.
        
        Flow:
        1. Get user ID from request
        2. Check Redis cache for 'user_{id}'
        3. If found, return cached data (fast, ~5ms)
        4. If not found, query database (slow, ~50ms)
        5. Save result to cache for 5 minutes
        6. Return data
        
        Cache key: 'user_{id}' (e.g., 'user_5')
        TTL: Configured in settings.CACHE_TTL (default 5 minutes)
        """
        # Step 1: Get user ID and create cache key
        user_id = kwargs.get('pk')
        cache_key = get_cache_key('user', user_id)
        
        # Step 2: Try to get from cache
        cached_data = cache.get(cache_key)
        
        # Step 3: If cache hit, return immediately
        if cached_data is not None:
            print(f"Cache HIT: Returning user {user_id} from cache")
            return Response(cached_data)
        
        # Step 4: Cache miss - get from database
        print(f"Cache MISS: Fetching user {user_id} from database...")
        response = super().retrieve(request, *args, **kwargs)
        
        # Step 5: Store in cache
        cache.set(cache_key, response.data, timeout=settings.CACHE_TTL)
        print(f"Cached user {user_id} for {settings.CACHE_TTL} seconds")
        
        # Step 6: Return response
        return response

    def perform_create(self, serializer):
        """
        Create user and invalidate list cache.
        
        Why: New user added, so cached user list is now stale.
        Clear the 'user_list' cache so next request gets fresh data.
        """
        # Clear the user list cache since we're adding a new user
        cache.delete(get_cache_key('user_list'))
        print("Cache cleared: user_list (new user created)")
        
        # Create the user in database
        super().perform_create(serializer)

    def perform_update(self, serializer):
        """
        Update user and invalidate both list and individual caches.
        
        Why: User data changed, so both caches are now stale.
        Clear both 'user_list' and 'user_{id}' caches.
        """
        user_id = serializer.instance.id
        
        # Clear both list cache and individual user cache
        cache.delete(get_cache_key('user_list'))
        cache.delete(get_cache_key('user', user_id))
        print(f"Cache cleared: user_list and user_{user_id} (user updated)")
        
        # Update the user in database
        super().perform_update(serializer)

    def perform_destroy(self, instance):
        """
        Delete user and invalidate both list and individual caches.
        
        Why: User deleted, so both caches are now stale.
        Clear both 'user_list' and 'user_{id}' caches.
        """
        user_id = instance.id
        
        # Clear both list cache and individual user cache
        cache.delete(get_cache_key('user_list'))
        cache.delete(get_cache_key('user', user_id))
        print(f"Cache cleared: user_list and user_{user_id} (user deleted)")
        
        # Delete the user from database
        super().perform_destroy(instance) 