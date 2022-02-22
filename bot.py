from re import findall
from rubika import Bot

bot = Bot("AUTH-TOKEN")
target = "GUID"

def hasInsult(msg):
	swData = [False,None]
	for i in open("dontReadMe.txt").read().split("\n"):
		if i in msg:
			swData = [True, i]
			break
		else: continue
	return swData

def hasAds(msg):
	links = list(map(lambda ID: ID.strip()[1:],findall("@[\w|_|\d]+", msg))) + list(map(lambda link:link.split("/")[-1],findall("rubika\.ir/\w+",msg)))
	joincORjoing = "joing" in msg or "joinc" in msg

	if joincORjoing: return joincORjoing
	else:
		for link in links:
			try:
				Type = bot.getInfoByUsername(link)["data"]["chat"]["abs_object"]["type"]
				if Type == "Channel":
					return True
			except KeyError: return False

# static variable
answered, sleeped, retries = [], False, {}

while True:
	try:
		admins = [i["member_guid"] for i in bot.getGroupAdmins(target)["data"]["in_chat_members"]]
		min_id = bot.getGroupInfo(target)["data"]["chat"]["last_message_id"]

		while True:
			try:
				messages = bot.getMessages(target,min_id)
				break
			except:
				continue

		open("id.txt","w").write(str(messages[-1].get("message_id")))

		for msg in messages:
			if msg["type"]=="Text" and not msg.get("message_id") in answered:
				if not sleeped:
					if hasInsult(msg.get("text"))[0] and not msg.get("author_object_guid") in admins :
						#ID = loads(c.decrypt(getUserInfo(msg.get("author_object_guid")).json().get("data_enc"))).get("data").get("user").get("username")
						#sendMessage(guid, f"#اخطار @{ID}", msg["message_id"])
						bot.deleteMessages(target, [str(msg.get("message_id"))])

					elif hasAds(msg.get("text")) and not msg.get("author_object_guid") in admins :
						bot.deleteMessages(target, [str(msg.get("message_id"))])

					elif "forwarded_from" in msg.keys() and bot.getMessagesInfo(target, [msg.get("message_id")])[0]["forwarded_from"]["type_from"] == "Channel" and not msg.get("author_object_guid") in admins :
						bot.deleteMessages(target, [str(msg.get("message_id"))])
						bot.sendMessage(target, "✅", message_id=msg.get("message_id"))

					elif msg.get("text") == "!sleep" and msg.get("author_object_guid") in admins :
						sleeped = True
						bot.sendMessage(target, "✅", message_id=msg.get("message_id"))

					elif msg.get("text") == "!del" and msg.get("author_object_guid") in admins :
						bot.deleteMessages(target, [msg.get("reply_to_message_id")])
						bot.sendMessage(target, "✅", message_id=msg.get("message_id"))

					elif msg.get("text").startswith("!ban") and msg.get("author_object_guid") in admins :
						try:
							guid = bot.getInfoByUsername(msg.get("text").split(" ")[1][1:])["data"]["chat"]["abs_object"]["object_guid"]
							if not guid in admins :
								bot.banGroupMember(target, guid)
								bot.sendMessage(target, "✅", message_id=msg.get("message_id"))
							else :
								bot.sendMessage(target, "❎", message_id=msg.get("message_id"))
								
						except IndexError:
							bot.banGroupMember(target, bot.getMessagesInfo(target, [msg.get("reply_to_message_id")])[0]["author_object_guid"])
							bot.sendMessage(target, "✅", message_id=msg.get("message_id"))

					elif msg.get("text").startswith("!send") :
						bot.sendMessage(bot.getInfoByUsername(msg.get("text").split(" ")[1][1:])["data"]["chat"]["object_guid"], "شما یک پیام ناشناس دارید:\n"+" ".join(msg.get("text").split(" ")[2:]))
						bot.sendMessage(target, "✅", message_id=msg.get("message_id"))

					elif msg.get("text").startswith("!add") :
						bot.invite(target, [bot.getInfoByUsername(msg.get("text").split(" ")[1][1:])["data"]["chat"]["object_guid"]])
						bot.sendMessage(target, "✅", message_id=msg.get("message_id"))

					elif msg.get("text") == "!lock" :
						print(bot.setMembersAccess(target, ["ViewMembers","ViewAdmins","AddMember"]).text)
						bot.sendMessage(target, "✅", message_id=msg.get("message_id"))

					elif msg.get("text") == "!unlock" :
						bot.setMembersAccess(target, ["ViewMembers","ViewAdmins","SendMessages","AddMember"])
						bot.sendMessage(target, "✅", message_id=msg.get("message_id"))

				else:
					if msg.get("text") == "!wakeup" and msg.get("author_object_guid") in admins :
						sleeped = False
						bot.sendMessage(target, "✅", message_id=msg.get("message_id"))

			elif msg["type"]=="Event" and not msg.get("message_id") in answered and not sleeped:
				name = bot.getGroupInfo(target)["data"]["group"]["group_title"]
				data = msg['event_data']
				if data["type"]=="RemoveGroupMembers":
					user = bot.getUserInfo(data['peer_objects'][0]['object_guid'])["data"]["user"]["first_name"]
					bot.sendMessage(target, f"بای بای {user} 🗑️", message_id=msg["message_id"])
				
				elif data["type"]=="AddedGroupMembers":
					user = bot.getUserInfo(data['peer_objects'][0]['object_guid'])["data"]["user"]["first_name"]
					bot.sendMessage(target, f"سلام {user} عزیز به گروه {name} خوش اومدی 😃\nلطفا قوانین رو رعایت کن 🥰", message_id=msg["message_id"])
				
				elif data["type"]=="LeaveGroup":
					user = bot.getUserInfo(data['performer_object']['object_guid'])["data"]["user"]["first_name"]
					bot.sendMessage(target, f"بای بای {user} 🗑️", message_id=msg["message_id"])
					
				elif data["type"]=="JoinedGroupByLink":
					user = bot.getUserInfo(data['performer_object']['object_guid'])["data"]["user"]["first_name"]
					bot.sendMessage(target, f"سلام {user} عزیز به گروه {name} خوش اومدی 😃\nلطفا قوانین رو رعایت کن 🥰", message_id=msg["message_id"])

			answered.append(msg.get("message_id"))

	except KeyboardInterrupt:
		exit()

	except Exception as e:
		if type(e) in list(retries.keys()):
			if retries[type(e)] < 3:
				retries[type(e)] += 1
				continue
			else:
				retries.pop(type(e))
		else:
			retries[type(e)] = 1
			continue