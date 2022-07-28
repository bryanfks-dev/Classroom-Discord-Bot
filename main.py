import discord
import nacl
import os
from datetime import datetime, timedelta
import time
import asyncio
import dic
import json
import pytz
from discord.ext import commands, tasks
from keep_alive import keep_alive

def prefix(client, message):
	return json.load(open("option.json", "r"))["prefix"]

def switch(client, message):
	return json.load(open("option.json", "r"))["switch"]

client = commands.Bot(command_prefix = prefix)

@client.event
async def on_ready():
	await client.change_presence(status=discord.Status.idle, activity=discord.Game('Lagi mantau jadwal kelas lo (Telah nganggur sejak 3 May 2022)'))
	print("Login as Classroom Discord Bot")

@client.event
async def on_command_error(ctx, error):
	if isinstance(error, commands.CommandOnCooldown):
		msg = 'sabarrr!! tunggu dlu {:.2f} detik'.format(error.retry_after)
		await ctx.send(msg)

@client.command()
async def ping(ctx):
	await ctx.send(embed = discord.Embed(title = f'{round(client.latency * 1000)} ms'))

@client.command()
async def prefix(ctx, arg = json.load(open("option.json", "r"))["prefix"]):
	old_prefix = json.load(open("option.json", "r"))["prefix"]	
	
	if old_prefix == arg:
		await ctx.send("kok prefixnya sama kek yg lama -_-")
	else:
		with open("option.json", "r") as jsonFile:
			data = json.load(jsonFile)

		data["prefix"] = arg
		with open("option.json", "w") as jsonFile:
			json.dump(data, jsonFile)

		embed = discord.Embed(title = f'Prefixnya diganti dari `{old_prefix}` jadi `{arg}`', color = discord.Color.blue())
		await ctx.send(embed = embed)

@client.command()
async def jadwal(ctx, arg = datetime.now(pytz.timezone("Asia/Singapore")).strftime("%A")):
	arg = [arg.lower()]

	now = datetime.now(pytz.timezone("Asia/Singapore")).strftime("%A").lower()
	day_list = [i for i in dic.day]

	if arg[0] == "tomorrow" or arg[0] == "besok":
		arg = [dic.day[day_list[day_list.index(now) + 1]]]

	elif arg[0] == "lusa":
		arg = [dic.day[day_list[day_list.index(now) + 2]]]

	elif arg[0] == "yesterday" or arg[0] == "kemarin":
		arg = [dic.day[day_list[day_list.index(now) - 1]]]

	elif arg[0] == "*":
		arg = day_list
		arg.pop(-1)

	embed = discord.Embed(title = "Jadwal", color = discord.Color.green())
	for i in arg:
		if i in dic.day or i in dic.day.values():
			if i in dic.day:
				day = dic.day[i]
			else:
				day = i

			if day == "minggu":
				await ctx.send("Lu yakin mau sekolah hari minggu?")
				return

			elif day != "kamis" and day != "sabtu":
				times = dic.timing["1"]
			
			elif day == "kamis":
				times = dic.timing["2"]

			else:
				times = dic.timing["3"]

		else:
			await ctx.send("Ngomong bahasa alien kah?")
			return

		classes = dic.subject[day]

		subs = []
		for i in range(0, len(times)):
			subs.append(f'{times[i]} | | {classes[i]} \n \n')

		desc = ""
		for j in subs:
			desc = desc + j

		if len(arg) > 1:
			embed.add_field(name = f'**{day.capitalize()}**', value = desc)
			continue
		else:
			embed = discord.Embed(title = day.capitalize(), description = f'**{desc}**', color = discord.Color.green())

	await ctx.send(embed = embed)

@client.command()
async def tanggal(ctx):
	calender = datetime.now(pytz.timezone("Asia/Singapore")).strftime("%A %d %B %Y")
	calender = calender.split(" ")
	await ctx.send(f'{dic.day[calender[0].lower()].capitalize()}, {calender[1]} {dic.month[calender[2]]} {calender[3]}')

@client.command()
async def cari(ctx, *, arg = "*"):
	if arg == "*":
		await ctx.send("cariin apa ?? -_-")
		return

	arg = arg.upper()

	if arg in dic.subject_list:
		embed = discord.Embed(title = f'Hasil pencarian : {arg}', color = discord.Color.green())

		days = [day for day in dic.day.values()]
		days.pop(-1)

		for i in days:
			if i != "kamis" and i != "sabtu":
				times = dic.timing["1"]
			
			elif i == "kamis":
				times = dic.timing["2"]

			else:
				times = dic.timing["3"]

			try:
				time_value = times[[j for j in dic.subject[i]].index(arg)]
				time_index = time_value.split(" - ")
				time_index = [datetime.strptime(j, "%H:%M") for j in time_index]

				if time_index[1] - time_index[0] > timedelta(minutes = 35):
					sub_val = "[2 Jam]"
				else:
					sub_val = "[1 Jam]"

				val = f'{time_value} <-- {sub_val}'

			except ValueError:
				val = "-"

			embed.add_field(name = i.capitalize(), value = val)

	else:
		await ctx.send("Pelajaran baru ?")
		return

	await ctx.send(embed = embed)	

@client.command()
async def sekarang(ctx):
	day = dic.day[datetime.now(pytz.timezone("Asia/Singapore")).strftime("%A").lower()]
	now = datetime.strptime(datetime.now(pytz.timezone("Asia/Singapore")).strftime("%H:%M"), "%H:%M")
	voice = client.get_channel(int(os.environ['VOICE_CHANNEL']))
	if day == "minggu":
		await ctx.send("Lu yakin mau sekolah hari minggu?")
		return
	elif day != "kamis" and day != "sabtu":
		times = dic.timing["1"]
		end = datetime.strptime("12:30", "%H:%M")
	elif day == "kamis":
		times = dic.timing["2"]
		end = datetime.strptime("12:30", "%H:%M")
	else:
		times = dic.timing["3"]
		end = datetime.strptime("10:15", "%H:%M")

	if now >= datetime.strptime("07:30", "%H:%M") and now <= end:
		if voice.members is not None:
			dates = []
			for i in [item.split(" - ") for item in times]:
				for j in i:
					dates.append(datetime.strptime(j, "%H:%M"))
			if (now >= datetime.strptime("09:25", "%H:%M") and now < datetime.strptime("09:35", "%H:%M")) or (now >= datetime.strptime("08:55", "%H:%M") and now < datetime.strptime("09:05", "%H:%M")):
				await ctx.send("Sekarang --> ISTIRAHAT 10 MENIT")
				return
			else:
				for k, l in enumerate(dates):
					if now == l:
						if l == dates[k + 1]:
							index = k + 1
						else:
							index = k
						break
					elif now < l:
						if l == dates[k + 1]:
							index = k + 1
						else:
							index = k	
						break
			await ctx.send(f'Sekarang --> {dic.subject[day][int(index/3)]}')
		else:
			await ctx.send("emng sklh ya?")
	else:
		await ctx.send("blom sekolah woi")

@client.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def kerkel(ctx):
	categoryCh = []
	category = client.get_channel(int(os.environ["CATEGORY"]))
	for channel in category.voice_channels:
		categoryCh.append(channel.name)
	if ctx.author.nick is None:
		name = f'Kelompok @{ctx.author.name}'
	else:
		name = f'Kelompok @{ctx.author.nick}'

	if name not in categoryCh:
		await ctx.guild.create_voice_channel(name = name, category = category, bitrate = 32000, rtc_region = discord.VoiceRegion.india)
		await ctx.send("channel dah dibuat")
	else:
		await ctx.send("lu masih ad channel lu sendiri woi, jgn serakah")
		return

	await asyncio.sleep(1)
	exist_vc = discord.utils.get(ctx.guild.channels, name=name)
	t = 30
	while t:
		if t == 10 and exist_vc.members == []:
			await ctx.send(f'channel lu bakal ilang klo ga ad org dlm {t} dtk')
		time.sleep(1)
		t -= 1
	if exist_vc.members == []:
		await exist_vc.delete()
		await ctx.send("channel lu dah ilang")

@client.command()
async def switch(ctx, arg = "work"):
	old_switch = json.load(open("option.json", "r"))["switch"]
	arg = arg.lower()
	if arg == "work":
		await ctx.send(f'Switch dalam kondisi `{old_switch}`')

	elif ctx.author.id == int(os.environ['OWNER']):
		if arg == "true" or arg == "false":
			if arg == old_switch:
				await ctx.send("kok modenya sama '=_=")
			else:
				with open("option.json", "r") as jsonFile:
					data = json.load(jsonFile)
				data["switch"] = arg
				with open("option.json", "w") as jsonFile:
					json.dump(data, jsonFile)
				await ctx.send("success!!")
		else:
			await ctx.send("?")
	else:
		await ctx.send("lu bukan yg ciptain gue, command ini cuman u/ owner")

@client.event
async def on_guild_channel_create(channel):
	if channel.category == client.get_channel(int(os.environ["CATEGORY"])) and type(channel) == discord.VoiceChannel:
		if not ch_check.is_running():
			ch_check.start()

async def time_check():
	if switch == "true":
		await client.wait_until_ready()
		voice = client.get_channel(int(os.environ['VOICE_CHANNEL']))
		while not client.is_closed():
			if voice.members != []:
					day = dic.day[datetime.now(pytz.timezone("Asia/Singapore")).strftime("%A").lower()]
					now = datetime.now(pytz.timezone("Asia/Singapore")).strftime("%H:%M:%S")

					if day != "kamis" and day != "sabtu":
						times = dic.timing["1"]	
					elif day == "kamis":
						times = dic.timing["2"]
					else:
						times = dic.timing["3"]

					timeList = []
					for i in [item.split(" - ") for item in times]:
						for j in i:
								timeList.append(j + ":00")
				
					if now in timeList:
						audio_player = await voice.connect()
						audio_player.play(discord.FFmpegPCMAudio(source = './audio.mp3'))

						while audio_player.is_playing():
							await asyncio.sleep(1.2)
						await audio_player.disconnect()
			await asyncio.sleep(1)

client.loop.create_task(time_check())

@tasks.loop(seconds = 1)
async def ch_check():
	guild = client.get_guild(int(os.environ["GUILD_ID"]))
	vc = client.get_channel(int(os.environ['CATEGORY'])).voice_channels
	if vc != []:
		await asyncio.sleep(10)
		for i in vc:
			channel = discord.utils.get(guild.channels, name = i.name, type = discord.ChannelType.voice)
			members = channel.members
			if members == []:
				await channel.delete()

keep_alive()
client.run(os.environ['TOKEN'])