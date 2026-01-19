
## Network Architecture Guidelines

- region should use `ap-southeast-3`

### subnet

- the subnet should split into multi categories: 
  - DMZ subnet: for public-facing resources like web servers, load balancers, etc. 
  - apps biz subnet: for application-facing resources like application servers, microservices, etc. 
  - devops subnet: for DevOps-facing resources like CI/CD servers, configuration management servers, etc.
  - database subnet: for database-facing resources like database servers, caches, etc. 
  - audit subnet: for audit resources like audit log collectors, audit processors, etc. 
  - development subnet: for development resources like dev servers, test servers, etc.

- the servie in devops should expose port to lb for internal access, and use acls to restrict access




- @docs/development/26-01-16/03-component-specifications.md instance count in Apps increase to 2
