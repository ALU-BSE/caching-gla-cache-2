SafeBoda Caching Implementation - Activity Answers
**Team Members:** Esther Sessenou, Sydney Walmawa
**Date:** January 21, 2026


## **Activity 1: Understanding Caching Concepts**


### **Theory Check**
Before diving into implementation, answer these questions:

1. **What is caching and why is it important?**
Caching is the process of storing frequently accessed data n a fast access storage, to reduce the time needed to retrieve it. Its important because it significantly improve performance, user expereince, and also reduces database load.

Benefits :

1.**Speed**: Reduces response time 
2.**scalability**: Allows handling more users without adding database resources
3.**Cost**: Reduces expensive database qureries and API calls

2. **What are the different types of caching?**
   - Database query caching
   - Template caching
   - View caching
   - Full-page caching

3. **Cache Invalidation Challenge**
   - What problems can arise with stale cached data?
   Users see outdated data, adnd hence face data inconsistencies between cache and databses

   - When should cache be cleared?
   Cache should be cleared when underlaying data is created, or updated, or after the TTL expires

