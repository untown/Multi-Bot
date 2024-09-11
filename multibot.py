import discord
from discord.ext import commands
import random
from datetime import timedelta
from typing import Optional
from discord import TextChannel
import asyncio
import requests
from discord import Embed, Colour
import re
from datetime import datetime
import time    
from discord.ext.commands import has_permissions, CheckFailure  
from discord import app_commands
import ast
import aiohttp
from discord.ui import View, Button, Modal, TextInput



intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.tree.command(name="lock", description="Locks a channel")
@app_commands.checks.has_permissions(manage_channels=True)
async def lock(interaction: discord.Interaction, channel: Optional[discord.TextChannel] = None):
    channel = channel or interaction.channel
    try:
        await channel.set_permissions(interaction.guild.default_role, send_messages=False)
        embed = discord.Embed(
            title=f"🔒 Locked {channel.name} channel",
            colour=discord.Colour.green()
        )
        await interaction.response.send_message(embed=embed)
    except discord.Forbidden:
        embed = discord.Embed(
            title="❌ I do not have permission to lock this channel.",
            colour=discord.Colour.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    except discord.HTTPException as e:
        embed = discord.Embed(
            title=f"❗ An error occurred: {e}",
            colour=discord.Colour.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

@lock.error
async def lock_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        embed = discord.Embed(
            title="❌ You don't have permissions to use this command.",
            colour=discord.Colour.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed(
            title=f"❗ An error occurred: {error}",
            colour=discord.Colour.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="unlock", description="Unlocks a channel")
@app_commands.checks.has_permissions(manage_channels=True)
async def unlock(interaction: discord.Interaction, channel: Optional[discord.TextChannel] = None):
    channel = channel or interaction.channel
    try:
        await channel.set_permissions(interaction.guild.default_role, send_messages=True)
        embed = discord.Embed(
            title=f"🔓 Unlocked {channel.name} channel",
            colour=discord.Colour.green()
        )
        await interaction.response.send_message(embed=embed)
    except discord.Forbidden:
        embed = discord.Embed(
            title="❌ I do not have permission to unlock this channel.",
            colour=discord.Colour.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    except discord.HTTPException as e:
        embed = discord.Embed(
            title=f"❗ An error occurred: {e}",
            colour=discord.Colour.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

@unlock.error
async def unlock_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        embed = discord.Embed(
            title="❌ You don't have permissions to use this command.",
            colour=discord.Colour.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed(
            title=f"❗ An error occurred: {error}",
            colour=discord.Colour.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="nuke", description="Deletes whole channel and creates same one")
@app_commands.checks.has_permissions(administrator=True)
async def nuke(interaction: discord.Interaction):
    channel = interaction.channel
    new_channel = await channel.clone(reason="Nuked the channel")
    
    await channel.delete(reason="Nuked the channel")
    
    embed = discord.Embed(
        title=f"💣 Channel {channel.name} has been nuked by `{interaction.user.display_name}`",
        colour=discord.Colour.yellow()
    )
    await new_channel.send(embed=embed)
    await new_channel.edit(position=channel.position)

    await interaction.response.send_message(embed=discord.Embed(title="Channel has been nuked!", colour=discord.Colour.yellow()))

@nuke.error
async def nuke_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        embed = discord.Embed(
            title="❌ You don't have permissions to use this command.",
            colour=discord.Colour.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed(
            title=f"❗ An error occurred: {error}",
            colour=discord.Colour.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="clear", description="Clears messages")
@app_commands.checks.has_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, amount: Optional[int] = None, reason: Optional[str] = None):
    await interaction.response.defer()
    
    if amount is None:
        embed = discord.Embed(
            title="❗Please specify the number of messages to delete.",
            colour=discord.Colour.yellow()
        )
        await interaction.followup.send(embed=embed)
        return

    if amount > 100:
        embed = discord.Embed(
            title="❗Amount is too large. Please keep it under `100`.",
            colour=discord.Colour.yellow()
        )
        await interaction.followup.send(embed=embed)
        return
    
    if amount <= 0:
        embed = discord.Embed(
            title="❗Please specify a positive number of messages to delete.",
            colour=discord.Colour.yellow()
        )
        await interaction.followup.send(embed=embed)
        return

    deleted = await interaction.channel.purge(limit=amount, reason=reason)
    embed = discord.Embed(
        title=f"🗑️ Successfully cleared `{len(deleted)}` messages.",
        colour=discord.Colour.yellow()
    )
    await interaction.followup.send(embed=embed)

@clear.error
async def clear_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        embed = discord.Embed(
            title="❌ You don't have permissions to use this command.",
            colour=discord.Colour.red()
        )
        await interaction.followup.send(embed=embed)
    elif isinstance(error, app_commands.CommandInvokeError):
        embed = discord.Embed(
            title="❗Please provide a valid number of messages to delete.",
            colour=discord.Colour.yellow()
        )
        await interaction.followup.send(embed=embed)
    else:
        embed = discord.Embed(
            title=f"❗ An error occurred: {error}",
            colour=discord.Colour.red()
        )
        await interaction.followup.send(embed=embed)

@bot.tree.command(name="kick", description="kicks a member")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, member: discord.Member, *, reason: str = None):
    reason = reason or "No reason provided"
    try:
        await member.kick(reason=reason)
        embed = discord.Embed(
            title=f"{member.display_name} got kicked!",
            description=f"Reason: {reason}",
            colour=discord.Colour.yellow()
        )
        await interaction.response.send_message(embed=embed)
    except discord.Forbidden:
        embed = discord.Embed(
            title="I do not have permission to kick this member.",
            colour=discord.Colour.yellow()
        )
        await interaction.response.send_message(embed=embed)
    except discord.HTTPException as e:
        embed = discord.Embed(
            title=f"An error occurred: {e}",
            colour=discord.Colour.yellow()
        )
        await interaction.response.send_message(embed=embed)

@kick.error
async def kick_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        embed = discord.Embed(
            title="You do not have permission to kick this member.",
            colour=discord.Colour.yellow()
        )
        await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ban", description="Bans a member from the server")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member, *, reason: Optional[str] = None):
    reason = reason or "No reason provided"
    try:
        await member.ban(reason=reason)
        embed = discord.Embed(
            title=f"{member.display_name} got banned!",
            description=f"Reason: {reason}",
            colour=discord.Colour.yellow()
        )
        await interaction.response.send_message(embed=embed)
    except discord.Forbidden:
        embed = discord.Embed(
            title="I do not have permission to ban this member.",
            colour=discord.Colour.yellow()
        )
        await interaction.response.send_message(embed=embed)
    except discord.HTTPException as e:
        embed = discord.Embed(
            title=f"An error occurred: {e}",
            colour=discord.Colour.yellow()
        )
        await interaction.response.send_message(embed=embed)

@ban.error
async def ban_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        embed = discord.Embed(
            title="You do not have permission to ban this member.",
            colour=discord.Colour.yellow()
        )
        await interaction.response.send_message(embed=embed)

@bot.tree.command(name="mute", description="Mutes a member for a specified duration")
@app_commands.checks.has_permissions(kick_members=True)
async def mute(interaction: discord.Interaction, member: discord.Member, time: str, *, reason: Optional[str] = None):
    reason = reason or "No reason provided"
    
    time_multiplier = {
        's': 1,
        'm': 60,
        'h': 3600,
        'd': 86400
    }
    
    unit = time[-1]
    if unit not in time_multiplier:
        embed = discord.Embed(
            title="Invalid time format! Use s, m, h, or d for seconds, minutes, hours, or days respectively.",
            colour=discord.Colour.yellow()
        )
        await interaction.response.send_message(embed=embed)
        return

    try:
        duration = int(time[:-1]) * time_multiplier[unit]
    except ValueError:
        embed = discord.Embed(
            title="Invalid time format! Make sure to specify a number followed by a unit (s, m, h, or d).",
            colour=discord.Colour.yellow()
        )
        await interaction.response.send_message(embed=embed)
        return

    timeout_until = discord.utils.utcnow() + timedelta(seconds=duration)

    try:
        await member.timeout(timeout_until, reason=reason)
        embed = discord.Embed(
            title=f"{member.display_name} has been muted for {time}",
            description=f"Reason: {reason}",
            colour=discord.Colour.yellow()
        )
        await interaction.response.send_message(embed=embed)
    except discord.Forbidden:
        embed = discord.Embed(
            title="I do not have permission to mute this member.",
            colour=discord.Colour.yellow()
        )
        await interaction.response.send_message(embed=embed)
    except discord.HTTPException as e:
        embed = discord.Embed(
            title=f"An error occurred: {e}",
            colour=discord.Colour.yellow()
        )
        await interaction.response.send_message(embed=embed)

@mute.error
async def mute_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        embed = discord.Embed(
            title="You don't have permissions to use this command.",
            colour=discord.Colour.yellow()
        )
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(
            title=f"An error occurred: {error}",
            colour=discord.Colour.yellow()
        )
        await interaction.response.send_message(embed=embed)

@bot.tree.command(name="unmute", description="Unmutes a member")
@app_commands.checks.has_permissions(kick_members=True)
async def unmute(interaction: discord.Interaction, member: discord.Member, *, reason: Optional[str] = None):
    reason = reason or "No reason provided"
    
    try:
        await member.timeout(None, reason=reason)
        embed = discord.Embed(
            title=f"{member.display_name} has been unmuted!",
            colour=discord.Colour.yellow()
        )
        await interaction.response.send_message(embed=embed)
    except discord.Forbidden:
        embed = discord.Embed(
            title="I do not have permission to unmute this member.",
            colour=discord.Colour.yellow()
        )
        await interaction.response.send_message(embed=embed)
    except discord.HTTPException as e:
        embed = discord.Embed(
            title=f"An error occurred: {e}",
            colour=discord.Colour.yellow()
        )
        await interaction.response.send_message(embed=embed)

@unmute.error
async def unmute_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        embed = discord.Embed(
            title="You don't have permissions to use this command.",
            colour=discord.Colour.yellow()
        )
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(
            title=f"An error occurred: {error}",
            colour=discord.Colour.yellow()
        )
        await interaction.response.send_message(embed=embed)

@bot.tree.command(name="addrole", description="Assign a role to a user")
@app_commands.checks.has_permissions(manage_roles=True)
async def addrole(interaction: discord.Interaction, user: discord.Member, role: discord.Role):
    if role in user.roles:
        embed = discord.Embed(
            title=f"{user.display_name} already has the role {role.name}",
            colour=discord.Colour.yellow()
        )
        await interaction.response.send_message(embed=embed)
    else:
        await user.add_roles(role)
        embed = discord.Embed(
            title=f"{user.display_name} was given the role {role.name}",
            colour=discord.Colour.yellow()
        )
        await interaction.response.send_message(embed=embed)

@addrole.error
async def addrole_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        embed = discord.Embed(
            title="You don't have permissions to use this command.",
            colour=discord.Colour.yellow()
        )
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(
            title=f"An error occurred: {error}",
            colour=discord.Colour.yellow()
        )
        await interaction.response.send_message(embed=embed)

@bot.tree.command(name="removerole", description="Remove a role from a user")
@app_commands.checks.has_permissions(manage_roles=True)
async def removerole(interaction: discord.Interaction, user: discord.Member, role: discord.Role):
    if role in user.roles:
        await user.remove_roles(role)
        embed = discord.Embed(
            title=f"{user.display_name} had the role {role.name} removed",
            colour=discord.Colour.yellow()
        )
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(
            title=f"{user.display_name} doesn't have the role {role.name}",
            colour=discord.Colour.yellow()
        )
        await interaction.response.send_message(embed=embed)

@removerole.error
async def removerole_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        embed = discord.Embed(
            title="You don't have permissions to use this command.",
            colour=discord.Colour.yellow()
        )
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(
            title=f"An error occurred: {error}",
            colour=discord.Colour.yellow()
        )
        await interaction.response.send_message(embed=embed)

@bot.tree.command(name="setnick", description="Change a member's nickname")
@app_commands.checks.has_permissions(manage_nicknames=True)
async def setnick(interaction: discord.Interaction, member: discord.Member, *, nick: str):
    try:
        await member.edit(nick=nick)
        embed = discord.Embed(
            title=f"Nickname changed to `{nick}`",
            colour=discord.Colour.yellow()
        )
        await interaction.response.send_message(embed=embed)
    except discord.Forbidden:
        embed = discord.Embed(
            title="I do not have permission to change this member's nickname.",
            colour=discord.Colour.yellow()
        )
        await interaction.response.send_message(embed=embed)
    except discord.HTTPException as e:
        embed = discord.Embed(
            title=f"An error occurred: {e}",
            colour=discord.Colour.yellow()
        )
        await interaction.response.send_message(embed=embed)

@setnick.error
async def setnick_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        embed = discord.Embed(
            title="You don't have permissions to use this command.",
            colour=discord.Colour.yellow()
        )
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(
            title=f"An error occurred: {error}",
            colour=discord.Colour.yellow()
        )
        await interaction.response.send_message(embed=embed)

@bot.tree.command(name="slow", description="Set the slowmode for the channel")
@app_commands.checks.has_permissions(manage_channels=True)
async def slow(interaction: discord.Interaction, time_str: str):
    seconds = parse_time(time_str)
    
    if seconds is None:
        embed = discord.Embed(
            title="Invalid time format. Choose one from: `5s`, `10s`, `15s`, `30s`, `1m`, `2m`, `5m`, `10m`, `15m`, `30m`, `1h`, `2h`, `6h`.",
            colour=discord.Colour.red()
        )
        await interaction.response.send_message(embed=embed)
        return
    
    await interaction.channel.edit(slowmode_delay=seconds)
    
    embed = discord.Embed(
        title=f"Slowmode set for this channel for {time_str}",
        colour=discord.Colour.yellow()
    )
    await interaction.response.send_message(embed=embed)

def parse_time(time_str):
    time_units = {
        's': {
            5: 5,
            10: 10,
            15: 15,
            30: 30
        },
        'm': {
            1: 60,
            2: 120,
            5: 300,
            10: 600,
            15: 900,
            30: 1800
        },
        'h': {
            1: 3600,
            2: 7200,
            6: 21600
        }
    }
    time_re = re.compile(r'(\d+)([smh])')
    matches = time_re.match(time_str)
    
    if matches:
        amount = int(matches.group(1))
        unit = matches.group(2)
        if unit in time_units and amount in time_units[unit]:
            return time_units[unit][amount]
    
    return None


@bot.tree.command(name="userinfo", description="Get information about the user")
async def userinfo(interaction: discord.Interaction):
    user = interaction.user
    inline = True
    embed = discord.Embed(title=f"{user.name}#{user.discriminator}", color=0x0080ff)
    userData = {
        "Mention": user.mention,
        "Nick": user.nick if user.nick else "None",
        "Created at": user.created_at.strftime("%b %d, %Y, %T"),
        "Joined at": user.joined_at.strftime("%b %d, %Y, %T"),
        "Server": interaction.guild.name,
        "Top role": user.top_role.name
    }
    for fieldName, fieldVal in userData.items():
        embed.add_field(name=fieldName + ":", value=fieldVal, inline=inline)
    embed.set_footer(text=f"ID: {user.id}")
    embed.set_thumbnail(url=user.display_avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="serverinfo", description="Get information about the server")
async def serverinfo(interaction: discord.Interaction):
    guild = interaction.guild
    embed = discord.Embed(
        title=f"Information for {guild.name}",
        colour=discord.Colour.blue()
    )
    embed.add_field(name="Server ID", value=guild.id)
    embed.add_field(name="Owner", value=guild.owner.mention)
    embed.add_field(name="Members", value=guild.member_count)
    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="clearslowmode", description="Clear the slowmode for the channel")
@app_commands.checks.has_permissions(manage_channels=True)
async def clearslowmode(interaction: discord.Interaction):
    await interaction.channel.edit(slowmode_delay=0)
    embed = discord.Embed(
        title="Slowmode has been cleared for this channel.",
        colour=discord.Colour.green()
    )
    await interaction.response.send_message(embed=embed)

welcome_channel_ids = {} 
welcome_messages = {} 


@bot.tree.command(name="setwelcome", description="Set the welcome message")
@app_commands.checks.has_permissions(manage_guild=True)
async def set_welcome_message(interaction: discord.Interaction, *, message: str):
    guild_id = interaction.guild.id
    welcome_messages[guild_id] = message
    embed = discord.Embed(
        title="Welcome message has been set.",
        colour=discord.Colour.yellow()
    )
    await interaction.response.send_message(embed=embed)

@set_welcome_message.error
async def set_welcome_message_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        embed = discord.Embed(
            title="You do not have permission to use this command.",
            colour=discord.Colour.red()
        )
        await interaction.response.send_message(embed=embed)
    else:
        raise error

@bot.tree.command(name="setwelcomechannel", description="Set the welcome channel")
@app_commands.checks.has_permissions(manage_guild=True)
async def set_welcome_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    guild_id = interaction.guild.id
    welcome_channel_ids[guild_id] = channel.id
    embed = discord.Embed(
        title="Welcome channel has been set.",
        colour=discord.Colour.yellow()
    )
    await interaction.response.send_message(embed=embed)

@set_welcome_channel.error
async def set_welcome_channel_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        embed = discord.Embed(
            title="You do not have permission to use this command.",
            colour=discord.Colour.red()
        )
        await interaction.response.send_message(embed=embed)
    else:
        raise error

def parse_time(time_str):
    time_units = {
        'd': 86400,  # 1 day = 86400 seconds
        'h': 3600,   # 1 hour = 3600 seconds
        'm': 60,     # 1 minute = 60 seconds
        's': 1       # 1 second = 1 second
    }
    time_re = re.compile(r'(\d+)([dhms])')
    total_seconds = 0
    matches = time_re.findall(time_str)

    for amount, unit in matches:
        if unit in time_units:
            total_seconds += int(amount) * time_units[unit]
        else:
            raise ValueError(f"Invalid time unit: {unit}")

    return total_seconds

enforced_nicknames = {}

@bot.tree.command(name='force_nickname', description='Enforce a nickname for a user')
@app_commands.checks.has_permissions(manage_nicknames=True)
async def force_nickname(interaction: discord.Interaction, member: discord.Member, *, nickname: str):
    try:
        await member.edit(nick=nickname)
        enforced_nicknames[member.id] = nickname
        embed = discord.Embed(
            title="Nickname Updated",
            description=f"Nickname for {member.mention} has been set to `{nickname}`.",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)
    except discord.Forbidden:
        embed = discord.Embed(
            title="Permission Denied",
            description="I don't have permission to change this user's nickname.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)
    except discord.HTTPException:
        embed = discord.Embed(
            title="Error",
            description="Failed to change the nickname due to an unexpected error.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)

@bot.event
async def on_member_update(before, after):
    if before.nick != after.nick and after.id in enforced_nicknames:
        expected_nick = enforced_nicknames[after.id]
        if after.nick != expected_nick:
            try:
                await after.edit(nick=expected_nick)
                embed = discord.Embed(
                    title="Nickname Reverted",
                    description=f"Your nickname has been set to `{expected_nick}`.",
                    color=discord.Color.green()
                )
                await after.send(embed=embed)
            except discord.Forbidden:
                pass
            except discord.HTTPException:
                pass


@bot.tree.command(name='remove_forced_nickname', description='Remove enforced nickname for a user')
@app_commands.checks.has_permissions(manage_nicknames=True)
async def remove_forced_nickname(interaction: discord.Interaction, member: discord.Member):
    if member.id in enforced_nicknames:
        del enforced_nicknames[member.id]
        await member.edit(nick=None)
        embed = discord.Embed(
            title="Nickname Removal",
            description=f"Enforced nickname for {member.mention} has been removed.",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(
            title="No Enforced Nickname",
            description=f"{member.mention} does not have an enforced nickname.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)

@bot.tree.command(name='avatar', description='Get the avatar of a user')
async def avatar(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user
    embed = discord.Embed(
        title=f"{member.name}'s Avatar",
        color=discord.Color.blue()
    )
    embed.set_image(url=member.avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='roleinfo', description='Get information about a role')
async def roleinfo(interaction: discord.Interaction, role: discord.Role):
    embed = discord.Embed(
        title=f"Role Info: {role.name}",
        color=role.color
    )
    embed.add_field(name="ID", value=role.id, inline=True)
    embed.add_field(name="Name", value=role.name, inline=True)
    embed.add_field(name="Color", value=str(role.color), inline=True)
    embed.add_field(name="Created At", value=role.created_at.strftime("%b %d, %Y, %T"), inline=True)
    embed.add_field(name="Hoist", value=role.hoist, inline=True)
    embed.add_field(name="Mentionable", value=role.mentionable, inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='servericon', description='Get the server icon')
async def servericon(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Server Icon",
        color=discord.Color.blue()
    )
    if interaction.guild.icon:
        embed.set_image(url=interaction.guild.icon.url)
    else:
        embed.title = "No Server Icon"
        embed.description = "This server does not have an icon."
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='serverroles', description='List all roles in the server')
async def serverroles(interaction: discord.Interaction):
    roles = [role.name for role in interaction.guild.roles if role.name != "@everyone"]
    role_list = "\n".join(roles)
    
    embed = discord.Embed(
        title="Server Roles",
        description=role_list or "No roles found.",
        color=discord.Color.blue()
    )
    await interaction.response.send_message(embed=embed)

sniped_messages = {}

@bot.event
async def on_message_delete(message):
    sniped_messages[message.channel.id] = message

@bot.tree.command(name='snipe', description='Get the last deleted message')
async def snipe(interaction: discord.Interaction):
    channel = interaction.channel
    if channel.id in sniped_messages:
        message = sniped_messages[channel.id]
        embed = discord.Embed(
            title=f"Sniped Message in #{channel.name}",
            description=message.content,
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Sent by {message.author}")
        await interaction.response.send_message(embed=embed)
        del sniped_messages[channel.id]  # Remove the sniped message after displaying it
    else:
        embed = discord.Embed(
            title="Nothing to Snipe",
            description="There's nothing to snipe!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)

@bot.tree.command(name='calculate', description='Evaluate a mathematical expression')
async def calculate(interaction: discord.Interaction, *, expression: str):
    try:
        # Use ast.literal_eval for safer evaluation
        result = ast.literal_eval(expression)
        
        # Embed for success
        embed = discord.Embed(
            title="Calculation Result",
            description=f"The result of `{expression}` is `{result}`.",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)
    except (ValueError, SyntaxError) as e:
        # Embed for error
        embed = discord.Embed(
            title="Error",
            description=f"Invalid expression: `{e}`.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        # Catch any other exceptions
        embed = discord.Embed(
            title="Error",
            description=f"An unexpected error occurred: `{e}`.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)

@bot.tree.command(name='listchannels', description='List all text and voice channels in the server')
async def listchannels(interaction: discord.Interaction):
    guild = interaction.guild

    # Gather text and voice channels
    text_channels = '\n'.join([f"📜 {text_channel.name}" for text_channel in guild.text_channels])
    voice_channels = '\n'.join([f"🎙️ {voice_channel.name}" for voice_channel in guild.voice_channels])
    
    # Create the embed
    embed = discord.Embed(
        title=f"Channels in {guild.name}",
        description=f"**Text Channels:**\n{text_channels or 'No text channels found.'}\n\n**Voice Channels:**\n{voice_channels or 'No voice channels found.'}",
        color=discord.Color.blue()
    )
    
    # Send the embed
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='8ball', description='Ask the Magic 8-Ball a question.')
async def _8ball(interaction: discord.Interaction, question: str):
    responses = [
        "It is certain.",
        "It is decidedly so.",
        "Without a doubt.",
        "Yes - definitely.",
        "You may rely on it.",
        "As I see it, yes.",
        "Most likely.",
        "Outlook good.",
        "Yes.",
        "Signs point to yes.",
        "Reply hazy, try again.",
        "Ask again later.",
        "Better not tell you now.",
        "Cannot predict now.",
        "Concentrate and ask again.",
        "Don't count on it.",
        "My reply is no.",
        "My sources say no.",
        "Outlook not so good.",
        "Very doubtful."
    ]

    answer = random.choice(responses)

    # Create the embed
    embed = discord.Embed(
        title="🎱 Magic 8-Ball",
        description=f"**Question:** {question}\n**Answer:** {answer}",
        color=discord.Color.blue()
    )
    
    # Send the embed as a response
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='banner', description='Get the banner of a user.')
async def banner(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user
    user = await bot.fetch_user(member.id)
    
    if user.banner:
        banner_url = user.banner.url
        embed = discord.Embed(
            title=f"{member.name}'s Banner",
            color=discord.Color.blue()
        )
        embed.set_image(url=banner_url)
    else:
        embed = discord.Embed(
            title=f"{member.name}'s Banner",
            description="This user does not have a banner.",
            color=discord.Color.blue()
        )

    await interaction.response.send_message(embed=embed)

vc_templates = {}
notification_channels = {}  # To store the notification channel for each guild

@bot.tree.command(name='set_template_channel', description='Set a voice channel as the template')
async def set_template_channel(interaction: discord.Interaction):
    guild = interaction.guild
    # Create a select menu for voice channels
    voice_channel_options = [
        discord.SelectOption(label=channel.name, value=str(channel.id))
        for channel in guild.voice_channels
    ]
    
    select = discord.ui.Select(
        placeholder="Select a voice channel to set as the template",
        min_values=1,
        max_values=1,
        options=voice_channel_options
    )
    
    async def select_callback(interaction: discord.Interaction):
        template_vc_id = int(select.values[0])
        template_channel = guild.get_channel(template_vc_id)

        if template_channel and isinstance(template_channel, discord.VoiceChannel):
            vc_templates[guild.id] = {
                'channel_id': template_vc_id,
                'category_id': template_channel.category_id,
                'permissions_synced': True  # Customize based on your needs
            }

            embed = discord.Embed(
                title="Template Channel Set",
                description=f"Voice channel `{template_channel.name}` set as the template.",
                color=discord.Color.green()
            )
            await interaction.response.edit_message(embed=embed, view=None)
        else:
            embed = discord.Embed(
                title="Invalid Voice Channel",
                description="Please select a valid voice channel.",
                color=discord.Color.red()
            )
            await interaction.response.edit_message(embed=embed, view=None)

    select.callback = select_callback

    view = discord.ui.View()
    view.add_item(select)

    await interaction.response.send_message(
        content="Please select a voice channel from the dropdown:",
        view=view
    )

@bot.event
async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
    guild_id = member.guild.id

    # Handle user joining the template channel
    if after.channel and after.channel.id == vc_templates.get(guild_id, {}).get('channel_id'):
        template_info = vc_templates.get(guild_id)

        if template_info is None:
            return  # No template set for this guild

        # Get category and permissions info from template
        category_id = template_info['category_id']
        permissions_synced = template_info['permissions_synced']

        # Create a new voice channel for the member
        new_vc_name = f"{member.display_name}'s Channel"
        overwrites = {member: discord.PermissionOverwrite(connect=True, mute_members=True, deafen_members=True)} if permissions_synced else None

        try:
            new_vc = await member.guild.create_voice_channel(
                name=new_vc_name,
                category=member.guild.get_channel(category_id),
                overwrites=overwrites
            )

            await member.move_to(new_vc)
            embed = discord.Embed(
                title="Custom Voice Channel Created",
                description=f"Custom voice channel `{new_vc.name}` has been created for {member.display_name}!",
                color=discord.Color.green()
            )
            notify_channel_id = notification_channels.get(guild_id)
            if notify_channel_id:
                notify_channel = member.guild.get_channel(notify_channel_id)
                if notify_channel:
                    await notify_channel.send(embed=embed)

        except discord.Forbidden:
            embed = discord.Embed(
                title="Permission Denied",
                description="I don't have permission to create voice channels.",
                color=discord.Color.red()
            )
            notify_channel_id = notification_channels.get(guild_id)
            if notify_channel_id:
                notify_channel = member.guild.get_channel(notify_channel_id)
                if notify_channel:
                    await notify_channel.send(embed=embed)
        except discord.HTTPException as e:
            embed = discord.Embed(
                title="Error",
                description=f"Failed to create voice channel: {str(e)}",
                color=discord.Color.red()
            )
            notify_channel_id = notification_channels.get(guild_id)
            if notify_channel_id:
                notify_channel = member.guild.get_channel(notify_channel_id)
                if notify_channel:
                    await notify_channel.send(embed=embed)

    # Handle user leaving a custom channel
    if before.channel and before.channel != after.channel:
        custom_channel = before.channel

        # Check if the channel was created by the bot
        if custom_channel.name.endswith("'s Channel") and len(custom_channel.members) == 0:
            try:
                await custom_channel.delete()
                embed = discord.Embed(
                    title="Custom Voice Channel Deleted",
                    description=f"The custom voice channel `{custom_channel.name}` was deleted because it was empty.",
                    color=discord.Color.orange()
                )
                notify_channel_id = notification_channels.get(guild_id)
                if notify_channel_id:
                    notify_channel = member.guild.get_channel(notify_channel_id)
                    if notify_channel:
                        await notify_channel.send(embed=embed)
            except discord.Forbidden:
                pass
            except discord.HTTPException as e:
                print(f"Failed to delete voice channel: {str(e)}")

@bot.tree.command(name='spotify', description='Check if a user is listening to Spotify')
async def spotify(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user
    for activity in member.activities:
        if isinstance(activity, discord.Spotify):
            embed = discord.Embed(
                title=f"{member.display_name} is listening to Spotify",
                description=f"[{activity.title}](https://open.spotify.com/track/{activity.track_id}) by {activity.artist}",
                color=0x1DB954
            )
            embed.set_thumbnail(url=activity.album_cover_url)
            embed.set_footer(text="Powered by Spotify", icon_url="https://cdn-icons-png.flaticon.com/512/174/174872.png")
            await interaction.response.send_message(embed=embed)
            return

    embed = discord.Embed(
        title=f"{member.display_name} is not listening to Spotify right now.",
        color=discord.Color.red()
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='game', description='Check if a user is playing a game')
async def game(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user
    for activity in member.activities:
        if isinstance(activity, discord.Game):
            embed = discord.Embed(
                title=f"{member.display_name} is playing a game",
                description=f"Playing **{activity.name}**",
                color=0x7289DA
            )
            # Set thumbnail if available or use a fallback icon
            embed.set_thumbnail(url=activity.large_image_url or "https://cdn-icons-png.flaticon.com/512/29/29514.png")
            await interaction.response.send_message(embed=embed)
            return

    embed = discord.Embed(
        title=f"{member.display_name} is not playing a game right now.",
        color=discord.Color.red()
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='hide', description='Hide the current channel from public view')
@app_commands.checks.has_permissions(manage_channels=True)
async def hide(interaction: discord.Interaction):
    channel = interaction.channel
    await channel.set_permissions(interaction.guild.default_role, view_channel=False)
    embed = discord.Embed(
        title=f"Channel {channel.name} Hidden",
        description=f"The channel {channel.name} has been hidden from public view.",
        color=discord.Color.green()
    )
    await interaction.response.send_message(embed=embed)

@hide.error
async def hide_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        embed = discord.Embed(
            title="Permission Denied",
            description="You do not have permission to manage channels.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed(
            title="Error",
            description=f"An error occurred: {str(error)}",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name='unhide', description='Make the current channel visible to everyone')
@app_commands.checks.has_permissions(manage_channels=True)
async def unhide(interaction: discord.Interaction):
    channel = interaction.channel
    await channel.set_permissions(interaction.guild.default_role, view_channel=True)
    embed = discord.Embed(
        title=f"Channel {channel.name} Unhidden",
        description=f"The channel {channel.name} is now visible to everyone.",
        color=discord.Color.green()
    )
    await interaction.response.send_message(embed=embed)

@unhide.error
async def unhide_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        embed = discord.Embed(
            title="Permission Denied",
            description="You do not have permission to manage channels.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed(
            title="Error",
            description=f"An error occurred: {str(error)}",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name='dice', description='Roll a six-sided die')
async def dice(interaction: discord.Interaction):
    roll = random.randint(1, 6)
    embed = discord.Embed(
        title=f"You rolled a `{roll}`",
        color=discord.Color.yellow()
    )
    await interaction.response.send_message(embed=embed)

settings = {
    "upload_channel": None,
    "staff_role": None,
    "pending_emojis": {}
}

class EmojiApprovalView(View):
    def __init__(self, user_id, bot):
        super().__init__()
        self.user_id = user_id
        self.bot = bot

    @discord.ui.button(label="Approve", style=discord.ButtonStyle.success)
    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check if the user has permission
        staff_role_id = settings.get("staff_role")
        if staff_role_id is None or not (interaction.user.guild_permissions.administrator or any(role.id == staff_role_id for role in interaction.user.roles)):
            await interaction.response.send_message("You do not have permission to approve emojis.", ephemeral=True)
            return

        if self.user_id not in settings["pending_emojis"]:
            await interaction.response.send_message("There is no pending emoji from this user.", ephemeral=True)
            return

        url, name, _ = settings["pending_emojis"].pop(self.user_id)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    await interaction.response.send_message("Failed to download the image.", ephemeral=True)
                    return
                data = await resp.read()

        emoji = await interaction.guild.create_custom_emoji(name=name, image=data)
        await interaction.response.send_message(f"Emoji {emoji} approved and added!")
        user = self.bot.get_user(self.user_id)
        if user:
            await user.send(f"Your emoji {emoji} has been approved!")

    @discord.ui.button(label="Deny", style=discord.ButtonStyle.danger)
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check if the user has permission
        staff_role_id = settings.get("staff_role")
        if staff_role_id is None or not (interaction.user.guild_permissions.administrator or any(role.id == staff_role_id for role in interaction.user.roles)):
            await interaction.response.send_message("You do not have permission to deny emojis.", ephemeral=True)
            return

        if self.user_id not in settings["pending_emojis"]:
            await interaction.response.send_message("There is no pending emoji from this user.", ephemeral=True)
            return

        settings["pending_emojis"].pop(self.user_id)
        await interaction.response.send_message(f"The emoji upload from {interaction.user.mention} has been denied.")
        user = self.bot.get_user(self.user_id)
        if user:
            await user.send("Your emoji upload has been denied.")

class EmojiModal(Modal):
    def __init__(self, bot):
        super().__init__(title="Upload Emoji")
        self.bot = bot

    file = TextInput(label="Upload a PNG file URL", style=discord.TextStyle.short)
    name = TextInput(label="Emoji Name", style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction):
        url = self.file.value
        name = self.name.value

        upload_channel_id = settings.get("upload_channel")
        if upload_channel_id is None:
            await interaction.response.send_message("The upload channel is not configured.", ephemeral=True)
            return

        if interaction.channel.id != upload_channel_id:
            await interaction.response.send_message(f"Please use the designated channel to upload emojis.", ephemeral=True)
            return
        
        if not url.lower().endswith(".png"):
            await interaction.response.send_message(f"The file must be a PNG image.", ephemeral=True)
            return
        
        if name in [emoji.name for emoji in interaction.guild.emojis]:
            await interaction.response.send_message(f"An emoji with that name already exists.", ephemeral=True)
            return
        
        settings["pending_emojis"][interaction.user.id] = (url, name, interaction.channel.id)
        
        embed = discord.Embed(title="New Emoji Pending Approval", description=f"**Name:** {name}\n**Uploaded by:** {interaction.user.mention}")
        embed.set_image(url=url)
        
        view = EmojiApprovalView(interaction.user.id, self.bot)
        
        staff_role_id = settings.get("staff_role")
        if staff_role_id is None:
            await interaction.response.send_message("The staff role is not configured.", ephemeral=True)
            return

        staff_role = interaction.guild.get_role(staff_role_id)
        if staff_role:
            await interaction.channel.send(content=f"{staff_role.mention} A new emoji '{name}' has been uploaded and is awaiting approval.", embed=embed, view=view)
        else:
            await interaction.response.send_message("The staff role could not be found.", ephemeral=True)
        
        await interaction.response.send_message("Your emoji is pending approval from the staff.", ephemeral=True)

@bot.tree.command(name="set_emoji_channel", description="sets the emoji channel to upload")
@commands.has_permissions(administrator=True)
async def set_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    settings["upload_channel"] = channel.id
    await interaction.response.send_message(f"Emoji upload channel set to {channel.mention}", ephemeral=True)

@bot.tree.command(name="set_staff_role", description="sets the role that can approve the emojis")
@commands.has_permissions(administrator=True)
async def set_staff_role(interaction: discord.Interaction, role: discord.Role):
    settings["staff_role"] = role.id
    await interaction.response.send_message(f"Staff role set to {role.mention}", ephemeral=True)

@bot.tree.command(name="upload_emoji")
async def upload_emoji(interaction: discord.Interaction):
    await interaction.response.send_modal(EmojiModal(bot))

bot.run("YOUR BOT TOKEN")