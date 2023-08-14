# Various architectures and pros and cons for our use case

## Microservices

### Pros

-  Better plug and play support.
-  Flexibility in using different languages and tools for each service.
-  Horizontal scalability.
-  Services can be deployed differently if required.
-  Parallel development.

### Cons

- Complexity of managing different services.
- Communication overhead between different services, deploying on same or nearby instances may reduce this.
- Coordinating the deployment of these multiple services can be challenging.


## Event driven 

### Pros

- Real time responsivness to events.
- Components loosely coupled, easier mainatanence.
- Good Horizontal scalability but lesser than Microservices.

### Cons

- Event ordering can be challenging.
- Our system does not seem to need real time response, but is more focussed on concurrency and integrity of data.
- Debugging challenges in event driven systems.
- Complexity of managing event sequencing.

## 