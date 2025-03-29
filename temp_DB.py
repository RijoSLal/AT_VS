import psycopg2 

def create_connection(): 
	# Connect to the database 
	# using the psycopg2 adapter. 
	# Pass your database name ,# username , password , 
	# hostname and port number 
	conn = psycopg2.connect(dbname='atvs', 
							user='postgres', 
							password='password', 
							host='localhost', 
							port='5432') 
	# Get the cursor object from the connection object 
	curr = conn.cursor() 
	return conn, curr 




def create_table(): 
	try: 
		# Get the cursor object from the connection object 
		conn, curr = create_connection() 
		try: 
			# Fire the CREATE query 
        
			curr.execute("CREATE TABLE IF NOT EXISTS confidential(ID INTEGER UNIQUE, name TEXT,Img BYTEA, data TEXT)") 
			
		except(Exception, psycopg2.Error) as error: 
			# Print exception 
			print("Error while creating confidential table", error) 
		finally: 
			# Close the connection object 
			conn.commit() 
			conn.close() 
	finally: 
		# Since we do not have to do anything here we will pass 
		pass

def write_blob(cartoonID, file_path, name, data): 
    try: 
        # read data from an image file
        with open(file_path, 'rb') as file:
            drawing = file.read()
        
        conn, cursor = create_connection() 
        
        try: 
            # Insert data into the table
            cursor.execute("""
                INSERT INTO confidential (ID, name, Img, data)
                VALUES (%s, %s, %s, %s)
            """, (cartoonID, name, psycopg2.Binary(drawing), data))
            
            # Commit changes
            conn.commit()
            print("Data inserted successfully.")
        except (Exception, psycopg2.DatabaseError) as error: 
            print("Error while inserting data in confidential table:", error) 
        finally: 
            # Close the connection
            conn.close() 
    except Exception as e:
        print("Error reading the image file:", e)

# Call the create table method	 
create_table() 
# Prepare sample data, of images, from local drive 
folder="temp_database_image"

write_blob(1,f"{folder}/john.jpg","John Wick","John Wick is the ultimate badass—feared, respected, and unstoppable. Known as Baba Yaga, he’s not just an assassin; he’s the nightmare of assassins. After losing his wife, a stolen car and a dead dog ignited his legendary wrath, wiping out the Russian mafia with sheer precision. His mastery of Gun-Fu, judo, and jiu-jitsu makes him a one-man army, taking down enemies with brutal efficiency. No matter how many times he’s shot, stabbed, or thrown off buildings, he keeps going, fueled by pure willpower. Even the deadliest killers and secret societies fear his name. Dressed in all black, silent yet deadly, he’s not just a hitman—he’s an unstoppable force") 
write_blob(2,f"{folder}/marquis.jpg","Marquis Vincent de Gramont","A high-ranking enforcer of the High Table, known for his strategic mind and ruthless execution of power. Personally tasked with eliminating John Wick, he orchestrated the destruction of the New York Continental and coerced retired assassin Caine into his service. Overconfident in his authority, he miscalculated his final confrontation, resulting in his elimination during a formal duel.") 
write_blob(3,f"{folder}/viggo.jpg","Viggo Tarasov"," Former head of the Tarasov Crime Syndicate, Viggo Tarasov was a powerful and feared crime lord with vast resources and a ruthless nature. He once mentored John Wick and respected his skills, referring to him as 'Baba Yaga.' After his son, Iosef, unknowingly provoked John by killing his dog and stealing his car, Viggo attempted to contain the situation but ultimately waged war against his former assassin. Despite his efforts, his forces were decimated, and he was fatally wounded in a final confrontation with John")
write_blob(4,f"{folder}/antonio.jpg","Santino D’Antonio","Santino D’Antonio is a ruthless and cunning member of the Italian Camorra crime syndicate. He holds a Marker over John Wick, a blood oath that binds John to fulfill a request. After forcing John to assassinate his own sister, Gianna D’Antonio, he betrays him and places a $7 million bounty on his head. Manipulative and power-hungry, Santino seeks to take control of the High Table, but his arrogance leads to his downfall when John breaks the sacred rules of the Continental and executes him in cold blood")

# write_blob(id,f"{folder}/image.jpg","name","description") 