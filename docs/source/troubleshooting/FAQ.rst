Frequently Asked Questions
==========================

-  Can I add storage to ECS-CommunityEdition after initializing an
   installation?

   No. Unfortunately because ECS Community Edition lacks the 'fabric'
   present in full featured ECS, it is not possible to add storage space
   after a completed installation.

-  I am locked out of my ECS management console, can I reset the root
   password?

   Currently there is no procedure to reset the root password if you are
   locked out.

-  The storage capacity statistics presented on the ECS dashboard seem
   wrong, what's going on here?

   ECS uses a data boxcarting strategy called "chunking". Chunks are
   pre-allocated when ECS is first initialized. When user data is
   written into ECS, pre-allocated chunks are filled and ECS
   pre-allocates however many new chunks ECS "thinks" would be best for
   the future based on what it knows about the past.

   Capacity statistics are calculated based on allocated and
   pre-allocated chunks at the time statistics are requested, and don't
   exactly reflect the actual amount of user data stored within ECS. We
   do this because it is a performance-enhancing heuristic that is a
   "good enough" representation of capacities without having to churn
   through the whole system to figure out the actual user data capacity
   numbers. In short, the numbers you are seeing are not designed to be
   exact, but are close estimates.
