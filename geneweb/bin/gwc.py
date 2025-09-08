#!/usr/bin/env python3
# Copyright (c) 1998-2007 INRIA
# Python rewrite of Geneweb gwc (compiler)

import sys
import os
import argparse
from typing import List, Dict, Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from lib.core.gwdb import open_database
from lib.definitions import Person, Family, Sex, Access
from lib.util.progress_bar import ProgressBar

class GenewebCompiler:
    """Geneweb database compiler"""
    
    def __init__(self, input_file: str, output_dir: str, verbose: bool = False):
        self.input_file = input_file
        self.output_dir = output_dir
        self.verbose = verbose
        self.persons = []
        self.families = []
    
    def compile(self):
        """Compile genealogy data"""
        print(f"Compiling {self.input_file} to {self.output_dir}")
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Parse input file
        self._parse_input()
        
        # Create database
        self._create_database()
        
        print("Compilation completed successfully")
    
    def _parse_input(self):
        """Parse input genealogy file"""
        print("Parsing input file...")
        
        # Simple parser for demonstration
        # In real implementation, this would parse GEDCOM or other formats
        with open(self.input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        current_person = None
        current_family = None
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            try:
                if line.startswith('PERSON:'):
                    if current_person:
                        self.persons.append(current_person)
                    current_person = self._parse_person_line(line)
                
                elif line.startswith('FAMILY:'):
                    if current_family:
                        self.families.append(current_family)
                    current_family = self._parse_family_line(line)
                
                elif current_person and line.startswith('  '):
                    self._parse_person_attribute(current_person, line.strip())
                
                elif current_family and line.startswith('  '):
                    self._parse_family_attribute(current_family, line.strip())
            
            except Exception as e:
                print(f"Error parsing line {line_num}: {e}")
                if self.verbose:
                    print(f"Line content: {line}")
        
        # Add last person/family
        if current_person:
            self.persons.append(current_person)
        if current_family:
            self.families.append(current_family)
        
        print(f"Parsed {len(self.persons)} persons and {len(self.families)} families")
    
    def _parse_person_line(self, line: str) -> Person:
        """Parse person line"""
        # PERSON: John DOE
        parts = line[8:].strip().split()
        first_name = parts[0] if parts else ""
        surname = " ".join(parts[1:]) if len(parts) > 1 else ""
        
        return Person(
            first_name=first_name,
            surname=surname,
            sex=Sex.NEUTER,
            access=Access.PUBLIC
        )
    
    def _parse_family_line(self, line: str) -> Family:
        """Parse family line"""
        # FAMILY: 1
        return Family()
    
    def _parse_person_attribute(self, person: Person, line: str):
        """Parse person attribute"""
        if line.startswith('SEX:'):
            sex_str = line[4:].strip().upper()
            if sex_str == 'M':
                person.sex = Sex.MALE
            elif sex_str == 'F':
                person.sex = Sex.FEMALE
        
        elif line.startswith('BIRTH:'):
            # Parse birth date
            pass
        
        elif line.startswith('DEATH:'):
            # Parse death date
            pass
    
    def _parse_family_attribute(self, family: Family, line: str):
        """Parse family attribute"""
        if line.startswith('MARRIAGE:'):
            # Parse marriage date
            pass
    
    def _create_database(self):
        """Create database from parsed data"""
        print("Creating database...")
        
        # Initialize database
        db = open_database(self.output_dir)
        
        # Add persons with progress bar
        if self.persons:
            progress = ProgressBar(len(self.persons), "Adding persons")
            for i, person in enumerate(self.persons):
                db.set_person(i, person)
                progress.update(i + 1)
            progress.finish()
        
        # Add families
        if self.families:
            progress = ProgressBar(len(self.families), "Adding families")
            for i, family in enumerate(self.families):
                db.set_family(i, family)
                progress.update(i + 1)
            progress.finish()
        
        # Commit changes
        print("Committing changes...")
        db.commit_patches()
        db.close()

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Geneweb Compiler')
    parser.add_argument('input_file', help='Input genealogy file')
    parser.add_argument('-o', '--output', default='./base', help='Output database directory')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('-f', '--force', action='store_true', help='Force overwrite existing database')
    
    args = parser.parse_args()
    
    # Check input file
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' does not exist")
        sys.exit(1)
    
    # Check output directory
    if os.path.exists(args.output) and not args.force:
        response = input(f"Output directory '{args.output}' exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Compilation cancelled")
            sys.exit(0)
    
    # Compile
    compiler = GenewebCompiler(args.input_file, args.output, args.verbose)
    try:
        compiler.compile()
    except Exception as e:
        print(f"Compilation failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
