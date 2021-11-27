from jwcrypto import jwt, jwk
import datetime

exportedKey = {"k":"n35sGEwOrRZaNIclk89IJ-Kvcc1l2JhfFeHNCS6UJ7I","kty":"oct"} #replace this with the generated key

def generateKey():
    key = jwk.JWK(generate='oct', size=256)
    print(key.export())


def createSignedToken(payload=None):
    expkey = exportedKey
    key = jwk.JWK(**expkey)

    currentTimestamp = datetime.datetime.today().timestamp()
    thresholdTime = 60*60*500 #60 = 60sec(1 min), 60*10 = 10min
    expTime = currentTimestamp + thresholdTime
    
    payloadDict = payload
    payloadDict['exp'] = expTime

    Token = jwt.JWT(header={"alg": "HS256"},
                    claims=payloadDict
                    )

    Token.make_signed_token(key)
    serializedToken = Token.serialize()

    #encrypt serialized signed token with same key
    Etoken = jwt.JWT(header={"alg": "A256KW", "enc": "A256CBC-HS512"},
                     claims=serializedToken)
    Etoken.make_encrypted_token(key)
    encryptedToken = Etoken.serialize()
    return encryptedToken


#decrypt token to get the data
def decryptToken(encryptedToken = None):
    currentTimestamp = datetime.datetime.today().timestamp()

    try:
        if encryptedToken:
            #import an exported key
            key = jwk.JWK(**exportedKey)
            
            e = encryptedToken
            ET = jwt.JWT(key=key, jwt=e)
            ST = jwt.JWT(key=key, jwt=ET.claims)
            return {"status": True, "claims": eval(ST.claims)}
    except Exception as e:
        return {"status": False, "message": str(e) }
        