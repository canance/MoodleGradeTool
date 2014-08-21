################## 
# Cory Nance
# Script to grade labs 
# 20 August 2014

import os; 
import sys;

def main():
	if len(sys.argv) < 2: 
		path = raw_input("Please enter the folder path: ");
	else:
		path = str(sys.argv[1]);
	#end if

	files = os.listdir(path);
	
	for f in files:
		
		# Moodle renames all submissions so they cannot be compiled as is. Luckily
		# it does include the original filename so we can paritition the string
		# and extract the original filename from it.  From there we can cp the file 
		# in order to compile and run.

		student = f.partition('_')[0];
		tempFile = path + "/" + f.partition('assignsubmission_file_')[2];
		realFile = path + "/" + f;
		className = tempFile.replace(".java", "").replace(path + "/","");

		print "##################################\n";
		print student;
		print realFile + "\n\n";


		cmds = [];
		cmds.append( "cp \"" + realFile + "\" \"" + tempFile + "\"" );
		cmds.append( "javac \"" + tempFile + "\"" );
		cmds.append( "cd \"" + path + "\" && " + "java \"" + className + "\"" );

		for c in cmds:
			os.system(c);



		raw_input("Press enter to continue...");
		
		cmds = [];
		cmds.append( "clear" );
		cmds.append( "rm -f " + tempFile );
		cmds.append( "less \"" + realFile + "\"");

		for c in cmds:
			os.system(c);

	#end for f in files
#end main



if __name__ == "__main__":
	main();
#end if