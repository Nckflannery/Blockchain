import hashlib
import json
import requests
import sys
from time import process_time


def proof_of_work(block):
    """
    Simple Proof of Work Algorithm
    Stringify the block and look for a proof.
    Loop through possibilities, checking each one against `valid_proof`
    in an effort to find a number that is a valid proof
    :return: A valid proof for the provided block
    """
    block_string = json.dumps(block, sort_keys=True)
    proof = 0
    while not valid_proof(block_string, proof):
        proof += 1
    return proof


def valid_proof(block_string, proof):
    """
    Validates the Proof:  Does hash(block_string, proof) contain 6
    leading zeroes?  Return true if the proof is valid
    :param block_string: <string> The stringified block to use to
    check in combination with `proof`
    :param proof: <int?> The value that when combined with the
    stringified previous block results in a hash that has the
    correct number of leading zeroes.
    :return: True if the resulting hash is a valid proof, False otherwise
    """
    guess = f"{block_string}{proof}".encode()
    guess_hash = hashlib.sha256(guess).hexdigest()
    return guess_hash[:4] == "0000"

if __name__ == '__main__':
    # What is the server address? IE `python3 miner.py https://server.com/api/`
    if len(sys.argv) > 1:
        node = sys.argv[1]
    else:
        node = "http://localhost:5000"

    # Load ID
    f = open("my_id.txt", "r")
    id = f.read()
    print(f'Welcome {id}, and good luck!\n')
    f.close()

    # Define coins variable for use in response later
    coins = 0
    # Timer variable for total time
    total_time = 0

    # Run forever until interrupted
    while True:
        r = requests.get(url=node + "/last_block")
        # Handle non-json response
        try:
            data = r.json()
        except ValueError:
            print("Error: Non-json response")
            print("Response returned:")
            print(r)
            break

        start_time = process_time()
        new_proof = proof_of_work(data['last_block'])
        finish_time = (process_time() - start_time)
        total_time += finish_time

        # When found, POST it to the server {"proof": new_proof, "id": id}
        post_data = {"proof": new_proof, "id": id}

        r = requests.post(url=node + "/mine", json=post_data)
        data = r.json()

        if data['message'] == 'New Block Created!':
            coins += 1
            print(data['message'])
            print(f'Congratulations {id}\nYou mined a coin in {finish_time:.02f} seconds.\nTotal Coins: {coins}')
            print(f'Total mining time: {total_time/60:.02f} minutes\n')
        else:
            print(data['message'])
