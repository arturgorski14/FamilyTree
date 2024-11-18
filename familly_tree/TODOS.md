# HIGHEST PRIORITY
## Order by DESC/ASC by clicking on the table header
## Search by age using property from Member class

# HIGH PRIORITY
## Improve views redability
## Redesign styles, template_tags and html in more organized manner
## Introduce aunt, uncle, cousins in details.html
## Link/Create members using tree-view in details

# MEDIUM PRIORITY
## Tree based structure for all members at once (can be done as version expandable by user)
## Possibility to add photo for family member
## Order members based on age instead of pk (in all_members and details)

# LOW PRIORITY
## Authorization
## Members are tied to user created family.
## View other user family.
## Merge families with other user or add other user to family.

# LOWEST PRIORITY
## Optimize retrieval of Members from db
## Rewrite front-end using vue or react
## Create read-model using redis or elasticsearch



"""
WITH RECURSIVE rectree AS (
  SELECT * 
    FROM tree 
   WHERE node_id = 1 
UNION ALL 
  SELECT t.* 
    FROM tree t 
    JOIN rectree
      ON t.parent_id = rectree.node_id
) SELECT * FROM rectree;
4.1. Retrieving Using Recursive Common Table Expressions: https://www.baeldung.com/sql/storing-tree-in-rdb
or use Dedicated Graph Database
"""
