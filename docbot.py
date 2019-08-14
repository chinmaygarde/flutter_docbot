#!/usr/bin/env python

import argparse
import tempfile
import os
import errno
import subprocess
import shutil
import sys

def GetRepoSHA(repository):
  version = subprocess.check_output([
    'git',
    '-C',
    repository,
    'rev-parse',
    'HEAD',
  ])

  return version.strip()

def CloneRepo(repo):
  temp_directory = tempfile.mkdtemp()
  assert os.path.exists(temp_directory)
  repo_location = os.path.join(temp_directory, 'engine')
  subprocess.check_call([
    'git',
    'clone',
    '--depth',
    '1',
    '-b',
    'master',
    repo,
    repo_location
  ])
  return repo_location

def GenerateDocumentation(repo):
  subprocess.check_call([
    'doxygen',
  ], cwd=repo)
  doc_location = os.path.join(repo, 'docs', 'doxygen', 'html')
  assert os.path.exists(doc_location)
  return doc_location

def UpdateSylink(target, link_name):
  try:
    os.symlink(target, link_name)
  except OSError, e:
    if e.errno == errno.EEXIST:
      os.remove(link_name)
      os.symlink(target, link_name)
    else:
      raise e

def CopyDirectory(source, destination):
  shutil.copytree(source, destination, symlinks=True)

def RemoveDirectory(source):
  shutil.rmtree(source)

def main():
  parser = argparse.ArgumentParser()

  parser.add_argument('--repo', help='The repo to pull from to get the Doxygen source', required=True)
  parser.add_argument('--doc-destination', help='The location to place the generated documentation.', required=True)
  parser.add_argument('--doc-symlink', help='The location to put the symlink to the generated documentation.', required=True)

  args = parser.parse_args();

  repo_location = CloneRepo(args.repo)
  repo_sha = GetRepoSHA(repo_location)
  doc_destination = os.path.join(args.doc_destination, repo_sha)

  if os.path.exists(doc_destination):
    UpdateSylink(doc_destination, args.doc_symlink)
    print 'Already generated documentation for the latest commit. Nothing to do.'
    RemoveDirectory(repo_location)
    return 0

  doc_location = GenerateDocumentation(repo_location)
  UpdateSylink(doc_destination, args.doc_symlink)

  CopyDirectory(doc_location, doc_destination)

  RemoveDirectory(doc_location)
  RemoveDirectory(repo_location)

  return 0

if __name__ == '__main__':
  sys.exit(main())
