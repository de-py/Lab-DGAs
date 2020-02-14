import random
import requests
from dns import reversename, resolver

"""
DGA Algo Steps

1. Cellular Automata Rule 30
DGA will use Cellular Automata (CA) rule 30 (using wrap method) 
to generate the initial domain candidate value. CA rules say for each 3 bits, 
generate a single bit, 0 or 1, based on the described rule. 
See function lookup_30 for the rule definition. (Output equals 30 in Binary)

Following the rule above, you are left with a hex string: a partial candidate.

2. TLD Decision
Count vowels in candidate (a or e). Mod total by 5 and use result as index for TLD array options.

3. Remove Vowels
Remove vowels from candidate

4. Confirm length
Greater than 15: Capture first 15 values from index.

Less than 9: Generate a random string (no vowels) for remaing length required.
    Insert to front of candidate.

5. Connect resulting candidate with TLD decision and return.


"""
# Simple http
def simple_http(domain) -> str:
    # print("second get")
    requests.get("http://%s/index.html" % domain)


# Pulls the seed from an http request. (Simulating any api...such as twitter trending hashtags.. where you can't predict the next one )
def get_seed() -> str:
    response = requests.get("http://192.168.182.135/seed.txt")
    # print(response.text.rstrip())
    return response.text.rstrip()

# DNS Query
def dns_query(domain:str) -> str:
    # print("trying to resolve")
    resolv = resolver.Resolver()
    # resolv.nameservers = ['192.168.182.135']
    try:
        d = str(resolv.query(domain, "A")[0])
        print(d)

    except:
        print("Someone is watching")
        exit()
    
    simple_http(domain)
    return d
    


# This function tries to update the zone files automatically to include new A records. 
def add_to_dns(val:str) -> None:
    if ".com" in val:
        os.system('echo "%s.    IN      A       192.168.182.135" >> /etc/bind/zones/db.com' % val)

    if ".press" in val:
        os.system('echo "%s.    IN      A       192.168.182.135" >> /etc/bind/zones/db.press' % val)

    if ".me" in val:
        os.system('echo "%s.    IN      A       192.168.182.135" >> /etc/bind/zones/db.me' % val)

    if ".cc" in val:
        os.system('echo "%s.    IN      A       192.168.182.135" >> /etc/bind/zones/db.cc' % val)

    if ".lan" in val:
        os.system('echo "%s.    IN      A       192.168.182.135" >> /etc/bind/zones/db.csc840.lan' % val)


    os.system("systemctl restart bind9")

    # Better to sleep to make sure service has time to restart
    os.system("sleep 2")


# Part of CA Rule 30 -> Returns a single value based on the 3 bit lookup
def lookup_30(val:str) ->str:
    if len(val) != 3:
        print("You needed to have 3 values only for lookups")
        exit()
    
    lookup = {
        "111": "0",
        "110": "0",
        "101": "0",
        "100": "1",
        "011": "1",
        "010": "1",
        "001": "1",
        "000": "0"
    }
    return lookup[val]

# Part of CA Rule 30 -> Finds the rule 30 response regardless of length 
def find_30(s:str) -> str:
    s_len = len(s)
    bin_len = s_len * 4
    bin_s = int(s,16)
    bin_s = format(bin_s, "0%db" % bin_len)
    bin_s = bin_s[-1] + bin_s + bin_s[1]
    counter = 0
    final = ''
    while counter <= bin_len-1:
        check = bin_s[counter] + bin_s[counter+1] + bin_s[counter+2]
        final += lookup_30(check)
        counter += 1

    return format(int(final,2),'0%dx' % s_len),final

# Generates a random string based on how many characters you need
def random_letters(str_len: int) -> str:
    alphabet_no_vowels = "b"
    final = ''
    for i in range(str_len):
        final += random.choice(alphabet_no_vowels)

    return final

# Second part of algorithm. Remove vowels, calculate TLD, check length
def calculate_domain(candidate: str) -> str:
   TLDs = ['csc840.lan', 'com', 'press', 'me', 'cc']

   # Count vowels. Mod 5 based on how many there are and pick a TLD from this.
   # Only need to count a and e because the results for candidate will only ever be hex digits.
   tld_index = candidate.count('a')
   tld_index += candidate.count('e')
   tld = TLDs[tld_index % 5]
   
   # Remove vowels
   candidate = candidate.replace('a','').replace('e','')

   # Correct length
   if len(candidate) > 15:
       candidate = candidate[0:15]
   
   if len(candidate) < 9:
       pad = 9-len(candidate)
       candidate = random_letters(pad) + candidate


   return candidate + "." + tld

# DGA function (sort of). Following CA rule, run second step of calculations. 
def ca_dga(nr: int, seed: str, pretty: bool, try_dns: bool) -> None:
    binary = None
    domains = []
    for i in range(nr):
        # Running cellular automata rule
        seed,binary = find_30(seed)
        
        # If you want to print cool binary designs, set Pretty to True.
        if pretty:
            print(binary)
        
        # Otherwise, operate as normal.
        else:
            val = calculate_domain(seed)
            domains.append(val)
            if try_dns:
                add_to_dns(val)
    return domains

def main():
    """
    Seed must be hexadecimal value
    Seed can be almost anything because the CA rule does a great job randomizing the rest. 
    If you want to be certain it is random, better to do a few tests with a given seed prior 
    to make sure nothing is duplicated after a period of time. This can be a problem 
    on occassion with a bad seed or a rule that lends itself to this more.
    """
    # seed = "84ef34dda6"
    seed = get_seed()

    """
    If True, this prints in binary instead of hex. Output to file and view with minimap in 
    something like VS code to see the designs that result from this. Pretty neat designs
    """
    pretty = False    

    # How many domains do you want to generate?
    how_many_loops = 1

    # Try_dns will try to update dns config file. 
    try_dns = False

    # Run DGA
    domains = ca_dga(how_many_loops,seed, pretty, try_dns) 

    for i in domains:
        j = dns_query(i)
        print("Seed: %s, domain: %s, DNS lookup: %s" % (seed,i,j))
        
    


if __name__ == "__main__":
    main()
