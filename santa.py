#!/usr/bin/env python3
import sys
import random
import shelve
import pdb

def extract_names():
	names = []
	families = []
	for line in sys.stdin:
		current = line.rstrip().split(',')
		if len(current) > 1:
			cleaned = [x.strip() for x in current]
			names += cleaned
			families.append(cleaned)
		if len(current) == 1:
			names.append(current[0])
	return (names, families)

def is_family(first, second):
	for family in families:
		if first != second and first in family and second in family:
			return True
	return False

def get_santa(name, recipients):
	def _get_santa(name, candidates):
		candidate = pick_random_name(candidates)
		if candidate:
			# not you
			if candidate != name:
				# not a couple
				if not is_family(name, candidate):
					prev = previous.get(name, '')
					# not a santa from previous run
					if prev != candidate:
						return candidate
			candidates.remove(candidate)
			return _get_santa(name, candidates)
	return _get_santa(name, list(recipients))

def pick_random_name(candidates):
	if candidates:
		if len(candidates) == 1:
			i = 0
		else:
			i = random.randint(0, len(candidates) - 1)
		return candidates[i]

def unassign_random_person(lst):
	senders = list(lst.keys())
	i = random.randint(0, len(senders) - 1)
	sender = senders[i]
	recipient = lst[sender]
	del lst[sender]
	return (lst, sender, recipient)

def persist_assignments(lst):
	with shelve.open('assignments') as f:
		f['lst'] = lst

def get_previous_assignments():
	with shelve.open('assignments') as f:
		return f.get('lst', {})

def pair_people():
	def _pair_people(lst, senders, recipients):
		unassigned = []
		for name in senders:
			santa = get_santa(name, recipients)
			if santa:
				lst[name] = santa
				recipients.remove(santa)
			else:
				unassigned.append(name)
		return (lst, unassigned, recipients)

	lst, senders, recipients = _pair_people({}, list(names), list(names))
	while len(senders) > 0:
		lst, sender, recipient = unassign_random_person(lst)
		senders.append(sender)
		recipients.append(recipient)
		lst, senders, recipients = _pair_people(lst, senders, recipients)

	persist_assignments(lst)
	return lst

names, families = extract_names()
previous = get_previous_assignments()
lst = pair_people()
for key, val in lst.items():
	print(key, '=>', val)
