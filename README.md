# privacy-preservation
Small distributed network to simulate privacy-preserving algorithms for distributed medical image processing.
Network is build out of Python microservices that communicate using Flask framework.

Including: Differential privacy (Laplace & Gaussian) and Homomorphic Encryption

Instruction:
1. Open three separate terminals
2. Run python3 _microservice1.py_ and _python3 microservice2.py_ in two separate terminals, to start the micro_services.
3. In the third terminal, start the evaluation by calling the preferred function. For example: _curl http://127.0.0.1:5010/evaluate_result_ (But adjust the IPadress and portnumber to match your machine)

Good luck!
