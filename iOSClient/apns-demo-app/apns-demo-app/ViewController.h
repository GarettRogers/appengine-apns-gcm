//
//  ViewController.h
//  apns-demo-app
//
//  Created by Garett Rogers on 13-04-16.
//  Copyright (c) 2013 AimX Labs. All rights reserved.
//

#import <UIKit/UIKit.h>

@interface ViewController : UIViewController
- (IBAction)registerForPush:(id)sender;
@property (weak, nonatomic) IBOutlet UIButton *RegisterButton;

@end
