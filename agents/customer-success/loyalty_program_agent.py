#!/usr/bin/env python3
"""
Loyalty Program Agent
=====================
Manages customer loyalty programs, tracks points, rewards, and membership tiers.
Handles rewards redemption, member management, and program analytics.
"""

import argparse
import json
import sys
import logging
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from collections import Counter

# Setup logging
LOG_DIR = Path("/home/clawbot/.openclaw/workspace/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - LOYALTY - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "loyalty_program.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Data paths
DATA_DIR = Path("/home/clawbot/.openclaw/workspace/data/customer-success")
DATA_DIR.mkdir(parents=True, exist_ok=True)
MEMBERS_FILE = DATA_DIR / "loyalty_members.json"
REWARDS_FILE = DATA_DIR / "rewards.json"
TRANSACTIONS_FILE = DATA_DIR / "point_transactions.json"
PROGRAM_FILE = DATA_DIR / "program_config.json"


def load_json(filepath: Path, default: dict = None) -> dict:
    """Load JSON file or return default."""
    if default is None:
        default = {}
    try:
        if filepath.exists():
            return json.loads(filepath.read_text())
    except Exception as e:
        logger.error(f"Error loading {filepath}: {e}")
    return default


def save_json(filepath: Path, data: dict) -> bool:
    """Save data to JSON file."""
    try:
        filepath.write_text(json.dumps(data, indent=2, default=str))
        return True
    except Exception as e:
        logger.error(f"Error saving {filepath}: {e}")
        return False


def init_data_files():
    """Initialize data files if they don't exist."""
    if not MEMBERS_FILE.exists():
        save_json(MEMBERS_FILE, {"members": []})
    
    if not REWARDS_FILE.exists():
        save_json(REWARDS_FILE, {
            "rewards": [
                {
                    "id": "discount_10",
                    "name": "10% Discount",
                    "description": "Get 10% off your next order",
                    "points_cost": 100,
                    "type": "discount",
                    "value": 10,
                    "active": True
                },
                {
                    "id": "discount_25",
                    "name": "25% Discount",
                    "description": "Get 25% off your next order",
                    "points_cost": 250,
                    "type": "discount",
                    "value": 25,
                    "active": True
                },
                {
                    "id": "free_shipping",
                    "name": "Free Shipping",
                    "description": "Free shipping on your next order",
                    "points_cost": 50,
                    "type": "shipping",
                    "value": 0,
                    "active": True
                },
                {
                    "id": "free_item",
                    "name": "Free Small Item",
                    "description": "Get a free item (under $10 value)",
                    "points_cost": 500,
                    "type": "product",
                    "value": 10,
                    "active": True
                }
            ]
        })
    
    if not TRANSACTIONS_FILE.exists():
        save_json(TRANSACTIONS_FILE, {"transactions": []})
    
    if not PROGRAM_FILE.exists():
        save_json(PROGRAM_FILE, {
            "program_name": "EmpireHazeClaw Rewards",
            "points_per_dollar": 1,
            "points_signup_bonus": 50,
            "tiers": [
                {"name": "Bronze", "min_points": 0, "discount": 0},
                {"name": "Silver", "min_points": 500, "discount": 5},
                {"name": "Gold", "min_points": 1000, "discount": 10},
                {"name": "Platinum", "min_points": 2500, "discount": 15}
            ],
            "created_at": datetime.now().isoformat()
        })


def get_member_tier(total_points: int, tiers: List[dict]) -> dict:
    """Determine member tier based on total points."""
    current_tier = tiers[0]
    for tier in tiers:
        if total_points >= tier['min_points']:
            current_tier = tier
    return current_tier


def cmd_dashboard(args) -> int:
    """Show loyalty program dashboard."""
    logger.info("Showing loyalty dashboard...")
    
    members = load_json(MEMBERS_FILE)
    rewards = load_json(REWARDS_FILE)
    transactions = load_json(TRANSACTIONS_FILE)
    program = load_json(PROGRAM_FILE)
    
    all_members = members.get('members', [])
    active_members = len([m for m in all_members if m.get('status') == 'active'])
    tiers = program.get('tiers', [])
    
    # Calculate tier distribution
    tier_dist = Counter()
    for m in all_members:
        tier = m.get('tier', 'Bronze')
        tier_dist[tier] += 1
    
    # Points statistics
    total_points_outstanding = sum(m.get('points_balance', 0) for m in all_members)
    total_points_earned = sum(m.get('total_points_earned', 0) for m in all_members)
    
    # Recent redemptions
    recent_trans = sorted(transactions.get('transactions', []), 
                         key=lambda x: x.get('created_at', ''), reverse=True)[:5]
    redemptions = [t for t in recent_trans if t.get('type') == 'redemption']
    
    print("\n" + "="*60)
    print("⭐ LOYALTY PROGRAM DASHBOARD")
    print("="*60)
    print(f"📅 Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Program: {program.get('program_name', 'Rewards Program')}")
    print("-"*60)
    
    print("\n👥 MEMBERS")
    print(f"   Total Members: {len(all_members)}")
    print(f"   Active: {active_members}")
    
    print("\n🏆 TIER DISTRIBUTION")
    for tier in tiers:
        count = tier_dist.get(tier['name'], 0)
        print(f"   {tier['name']:<10} {count:>4} members (min: {tier['min_points']} pts)")
    
    print("\n💎 POINTS METRICS")
    print(f"   Total Points Issued: {total_points_earned:,}")
    print(f"   Points Outstanding: {total_points_outstanding:,}")
    print(f"   Points per Dollar: {program.get('points_per_dollar', 1)}")
    
    print("\n🎁 REWARDS")
    active_rewards = len([r for r in rewards.get('rewards', []) if r.get('active', True)])
    print(f"   Active Rewards: {active_rewards}")
    print(f"   Total Redemptions: {len([t for t in transactions.get('transactions', []) if t.get('type') == 'redemption'])}")
    
    if redemptions:
        print("\n📅 RECENT REDEMPTIONS:")
        for t in redemptions[:3]:
            print(f"      🎁 {t.get('member_name', 'Unknown')} redeemed {t.get('reward_name', 'Reward')}")
    
    print("\n" + "="*60)
    return 0


def cmd_register_member(args) -> int:
    """Register a new loyalty member."""
    logger.info(f"Registering member: {args.email}")
    
    members = load_json(MEMBERS_FILE)
    program = load_json(PROGRAM_FILE)
    
    # Check if already registered
    for m in members.get('members', []):
        if m.get('email') == args.email:
            print(f"⚠️  Member {args.email} is already registered!")
            print(f"   Member ID: {m.get('id')}")
            print(f"   Current Points: {m.get('points_balance', 0)}")
            return 0
    
    # Get signup bonus
    signup_bonus = program.get('points_signup_bonus', 50)
    tiers = program.get('tiers', [])
    initial_tier = get_member_tier(signup_bonus, tiers)
    
    member = {
        "id": str(uuid.uuid4())[:8],
        "name": args.name,
        "email": args.email,
        "phone": args.phone,
        "points_balance": signup_bonus,
        "total_points_earned": signup_bonus,
        "total_points_redeemed": 0,
        "tier": initial_tier['name'],
        "status": "active",
        "member_since": datetime.now().isoformat(),
        "last_activity": datetime.now().isoformat(),
        "referral_code": str(uuid.uuid4())[:8],
        "notes": args.notes or ""
    }
    
    members['members'].append(member)
    save_json(MEMBERS_FILE, members)
    
    print(f"✅ Member registered!")
    print(f"   ID: {member['id']}")
    print(f"   Name: {args.name}")
    print(f"   Email: {args.email}")
    print(f"   Welcome Bonus: {signup_bonus} points!")
    print(f"   Tier: {initial_tier['name']}")
    
    return 0


def cmd_list_members(args) -> int:
    """List loyalty members."""
    logger.info("Listing members...")
    
    members = load_json(MEMBERS_FILE)
    all_members = members.get('members', [])
    
    # Apply filters
    if args.tier:
        all_members = [m for m in all_members if m.get('tier') == args.tier]
    if args.status:
        all_members = [m for m in all_members if m.get('status') == args.status]
    
    if not all_members:
        print("No members found.")
        return 0
    
    print(f"\n👥 Members ({len(all_members)}):")
    print("-"*70)
    for m in sorted(all_members, key=lambda x: x.get('points_balance', 0), reverse=True):
        tier_icon = {"Bronze": "🥉", "Silver": "🥈", "Gold": "🥇", "Platinum": "💎"}.get(
            m.get('tier', 'Bronze'), "❓")
        print(f"   {tier_icon} {m.get('name', 'Unknown'):<20} | {m.get('email', '?')}")
        print(f"       Points: {m.get('points_balance', 0):,} | Tier: {m.get('tier', '?')} | Status: {m.get('status', '?')}")
    
    return 0


def cmd_add_points(args) -> int:
    """Add points to a member's account."""
    logger.info(f"Adding {args.points} points to {args.member_id}")
    
    members = load_json(MEMBERS_FILE)
    transactions = load_json(TRANSACTIONS_FILE)
    program = load_json(PROGRAM_FILE)
    
    member = None
    for m in members.get('members', []):
        if m.get('id') == args.member_id or m.get('email') == args.member_id:
            member = m
            break
    
    if not member:
        print(f"❌ Member {args.member_id} not found.")
        return 1
    
    points_to_add = int(args.points)
    
    # Update member points
    member['points_balance'] += points_to_add
    member['total_points_earned'] += points_to_add
    member['last_activity'] = datetime.now().isoformat()
    
    # Check for tier upgrade
    tiers = program.get('tiers', [])
    new_tier = get_member_tier(member['total_points_earned'], tiers)
    old_tier = member.get('tier')
    
    if new_tier['name'] != old_tier:
        member['tier'] = new_tier['name']
        print(f"🎉 TIER UPGRADE! {old_tier} → {new_tier['name']}")
    
    save_json(MEMBERS_FILE, members)
    
    # Record transaction
    transaction = {
        "id": str(uuid.uuid4())[:8],
        "member_id": member['id'],
        "member_name": member['name'],
        "type": "earn",
        "points": points_to_add,
        "balance_after": member['points_balance'],
        "reason": args.reason or "Purchase",
        "order_id": args.order_id,
        "created_at": datetime.now().isoformat()
    }
    transactions['transactions'].append(transaction)
    save_json(TRANSACTIONS_FILE, transactions)
    
    print(f"✅ Added {points_to_add} points!")
    print(f"   New Balance: {member['points_balance']} points")
    print(f"   Tier: {member['tier']}")
    
    return 0


def cmd_redeem(args) -> int:
    """Redeem points for a reward."""
    logger.info(f"Redeeming reward: {args.reward_id} for {args.member_id}")
    
    members = load_json(MEMBERS_FILE)
    rewards = load_json(REWARDS_FILE)
    transactions = load_json(TRANSACTIONS_FILE)
    
    # Find member
    member = None
    for m in members.get('members', []):
        if m.get('id') == args.member_id or m.get('email') == args.member_id:
            member = m
            break
    
    if not member:
        print(f"❌ Member {args.member_id} not found.")
        return 1
    
    # Find reward
    reward = None
    for r in rewards.get('rewards', []):
        if r.get('id') == args.reward_id:
            reward = r
            break
    
    if not reward:
        print(f"❌ Reward {args.reward_id} not found.")
        return 1
    
    if not reward.get('active', True):
        print(f"❌ Reward {reward.get('name')} is no longer available.")
        return 1
    
    points_cost = reward.get('points_cost', 0)
    
    if member.get('points_balance', 0) < points_cost:
        print(f"❌ Insufficient points!")
        print(f"   Required: {points_cost}")
        print(f"   Available: {member.get('points_balance', 0)}")
        return 1
    
    # Process redemption
    member['points_balance'] -= points_cost
    member['total_points_redeemed'] += points_cost
    member['last_activity'] = datetime.now().isoformat()
    save_json(MEMBERS_FILE, members)
    
    # Record transaction
    transaction = {
        "id": str(uuid.uuid4())[:8],
        "member_id": member['id'],
        "member_name": member['name'],
        "type": "redemption",
        "points": -points_cost,
        "balance_after": member['points_balance'],
        "reward_id": reward['id'],
        "reward_name": reward['name'],
        "created_at": datetime.now().isoformat()
    }
    transactions['transactions'].append(transaction)
    save_json(TRANSACTIONS_FILE, transactions)
    
    # Generate coupon code
    coupon_code = f"LOYALTY-{member['id'].upper()}-{str(uuid.uuid4())[:4].upper()}"
    
    print(f"✅ Redemption successful!")
    print(f"   Reward: {reward.get('name')}")
    print(f"   Points Used: {points_cost}")
    print(f"   Remaining Balance: {member['points_balance']} points")
    print(f"   Coupon Code: {coupon_code}")
    
    return 0


def cmd_list_rewards(args) -> int:
    """List available rewards."""
    logger.info("Listing rewards...")
    
    rewards = load_json(REWARDS_FILE)
    all_rewards = rewards.get('rewards', [])
    
    if args.active_only:
        all_rewards = [r for r in all_rewards if r.get('active', True)]
    
    if not all_rewards:
        print("No rewards available.")
        return 0
    
    print(f"\n🎁 Available Rewards ({len(all_rewards)}):")
    print("-"*60)
    for r in sorted(all_rewards, key=lambda x: x.get('points_cost', 0)):
        status = "🟢" if r.get('active', True) else "🔴"
        print(f"   {status} {r.get('name', 'Untitled')}")
        print(f"       Cost: {r.get('points_cost', 0)} points | Type: {r.get('type', '?')}")
        print(f"       {r.get('description', '')}")
    
    return 0


def cmd_add_reward(args) -> int:
    """Add a new reward."""
    logger.info(f"Adding reward: {args.name}")
    
    rewards = load_json(REWARDS_FILE)
    
    reward = {
        "id": args.name.lower().replace(' ', '_')[:20],
        "name": args.name,
        "description": args.description or "",
        "points_cost": int(args.points_cost),
        "type": args.reward_type or "discount",
        "value": int(args.value) if args.value else 0,
        "active": True,
        "created_at": datetime.now().isoformat()
    }
    
    rewards['rewards'].append(reward)
    save_json(REWARDS_FILE, rewards)
    
    print(f"✅ Reward added: {args.name} ({args.points_cost} points)")
    return 0


def cmd_transactions(args) -> int:
    """Show transaction history."""
    logger.info("Showing transactions...")
    
    transactions = load_json(TRANSACTIONS_FILE)
    all_trans = transactions.get('transactions', [])
    
    # Filter by member
    if args.member_id:
        all_trans = [t for t in all_trans if t.get('member_id') == args.member_id]
    
    # Filter by type
    if args.type:
        all_trans = [t for t in all_trans if t.get('type') == args.type]
    
    # Filter by date range
    if args.days:
        cutoff = datetime.now() - timedelta(days=int(args.days))
        all_trans = [t for t in all_trans 
                     if datetime.fromisoformat(t.get('created_at', '2020-01-01')) > cutoff]
    
    if not all_trans:
        print("No transactions found.")
        return 0
    
    print(f"\n💳 Transactions ({len(all_trans)}):")
    print("-"*70)
    for t in sorted(all_trans, key=lambda x: x.get('created_at', ''), reverse=True)[:20]:
        type_icon = "➕" if t.get('type') == 'earn' else "🎁"
        points = t.get('points', 0)
        print(f"   {type_icon} {t.get('member_name', 'Unknown'):<15} | {points:>+6} pts | {t.get('created_at', '')[:10]}")
        if t.get('reason'):
            print(f"       Reason: {t.get('reason')}")
        if t.get('reward_name'):
            print(f"       Reward: {t.get('reward_name')}")
    
    return 0


def cmd_member_details(args) -> int:
    """Show detailed member information."""
    logger.info(f"Showing details for member: {args.member_id}")
    
    members = load_json(MEMBERS_FILE)
    transactions = load_json(TRANSACTIONS_FILE)
    program = load_json(PROGRAM_FILE)
    
    member = None
    for m in members.get('members', []):
        if m.get('id') == args.member_id or m.get('email') == args.member_id:
            member = m
            break
    
    if not member:
        print(f"❌ Member {args.member_id} not found.")
        return 1
    
    # Get member transactions
    member_trans = [t for t in transactions.get('transactions', []) 
                    if t.get('member_id') == member['id']]
    
    tiers = program.get('tiers', [])
    current_tier = next((t for t in tiers if t['name'] == member.get('tier')), tiers[0])
    next_tier = None
    for t in tiers:
        if t['min_points'] > current_tier['min_points']:
            next_tier = t
            break
    
    points_to_next = (next_tier['min_points'] - member.get('total_points_earned', 0)) if next_tier else 0
    
    print("\n" + "="*60)
    print(f"👤 MEMBER DETAILS - {member.get('name', 'Unknown')}")
    print("="*60)
    print(f"ID: {member['id']}")
    print(f"Email: {member.get('email', '?')}")
    print(f"Phone: {member.get('phone', 'Not provided')}")
    print("-"*60)
    
    print("\n💎 MEMBERSHIP")
    tier_icon = {"Bronze": "🥉", "Silver": "🥈", "Gold": "🥇", "Platinum": "💎"}.get(
        member.get('tier', 'Bronze'), "❓")
    print(f"   Tier: {tier_icon} {member.get('tier', 'Bronze')}")
    print(f"   Member Since: {member.get('member_since', '')[:10]}")
    print(f"   Status: {member.get('status', 'active')}")
    
    print("\n💰 POINTS")
    print(f"   Current Balance: {member.get('points_balance', 0):,} points")
    print(f"   Total Earned: {member.get('total_points_earned', 0):,}")
    print(f"   Total Redeemed: {member.get('total_points_redeemed', 0):,}")
    
    if next_tier:
        print(f"\n🎯 NEXT TIER: {next_tier['name']}")
        print(f"   Points needed: {points_to_next:,}")
        print(f"   Discount: {next_tier['discount']}%")
    
    print(f"\n🎁 REFERRAL CODE: {member.get('referral_code', 'N/A')}")
    
    print(f"\n📊 TRANSACTION SUMMARY")
    earn_trans = len([t for t in member_trans if t.get('type') == 'earn'])
    redeem_trans = len([t for t in member_trans if t.get('type') == 'redemption'])
    print(f"   Total Transactions: {len(member_trans)}")
    print(f"   Points Earned: {earn_trans}")
    print(f"   Redemptions: {redeem_trans}")
    
    print("\n" + "="*60)
    return 0


def cmd_stats(args) -> int:
    """Show loyalty program statistics."""
    logger.info("Calculating program statistics...")
    
    members = load_json(MEMBERS_FILE)
    rewards = load_json(REWARDS_FILE)
    transactions = load_json(TRANSACTIONS_FILE)
    program = load_json(PROGRAM_FILE)
    
    all_members = members.get('members', [])
    all_trans = transactions.get('transactions', [])
    all_rewards = rewards.get('rewards', [])
    
    # Calculate metrics
    total_members = len(all_members)
    active_members = len([m for m in all_members if m.get('status') == 'active'])
    
    total_points_earned = sum(t.get('points', 0) for t in all_trans if t.get('type') == 'earn')
    total_points_redeemed = abs(sum(t.get('points', 0) for t in all_trans if t.get('type') == 'redemption'))
    
    total_redemptions = len([t for t in all_trans if t.get('type') == 'redemption'])
    redemption_rate = (total_redemptions / len(all_members) * 100) if all_members else 0
    
    # Points by tier
    tier_points = {}
    for m in all_members:
        tier = m.get('tier', 'Bronze')
        tier_points[tier] = tier_points.get(tier, 0) + m.get('points_balance', 0)
    
    # Most redeemed rewards
    reward_counts = Counter(t.get('reward_name') for t in all_trans if t.get('type') == 'redemption')
    
    print("\n" + "="*60)
    print("📊 LOYALTY PROGRAM STATISTICS")
    print("="*60)
    print(f"Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("-"*60)
    
    print("\n👥 MEMBER STATS")
    print(f"   Total Members: {total_members}")
    print(f"   Active Members: {active_members}")
    print(f"   Inactive: {total_members - active_members}")
    
    print("\n💰 POINTS STATS")
    print(f"   Total Points Issued: {total_points_earned:,}")
    print(f"   Total Points Redeemed: {total_points_redeemed:,}")
    print(f"   Outstanding Points: {total_points_earned - total_points_redeemed:,}")
    print(f"   Redemption Rate: {redemption_rate:.1f}%")
    
    print("\n🎁 REWARD STATS")
    print(f"   Total Redemptions: {total_redemptions}")
    print(f"   Active Rewards: {len([r for r in all_rewards if r.get('active', True)])}")
    
    if reward_counts:
        print("\n🏆 TOP REDEEMED REWARDS")
        for reward, count in reward_counts.most_common(5):
            print(f"   {reward}: {count} redemptions")
    
    print("\n💎 POINTS BY TIER")
    tiers = program.get('tiers', [])
    for tier in tiers:
        pts = tier_points.get(tier['name'], 0)
        print(f"   {tier['name']:<10} {pts:>10,} points")
    
    print("\n" + "="*60)
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="⭐ Loyalty Program Agent - Customer Rewards Management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s dashboard                    Show loyalty dashboard
  %(prog)s register --email user@example.com --name "John Doe"
  %(prog)s list-members --tier Gold
  %(prog)s add-points --member-id abc123 --points 100 --reason "Purchase"
  %(prog)s redeem --member-id abc123 --reward-id discount_10
  %(prog)s list-rewards --active-only
  %(prog)s add-reward --name "VIP Support" --points-cost 1000 --type service
  %(prog)s transactions --days 30
  %(prog)s member-details --member-id abc123
  %(prog)s stats                        Show program statistics
        """
    )
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Dashboard
    subparsers.add_parser('dashboard', help='Show loyalty dashboard')
    
    # Member commands
    reg_parser = subparsers.add_parser('register', help='Register new member')
    reg_parser.add_argument('--email', required=True, help='Member email')
    reg_parser.add_argument('--name', required=True, help='Member name')
    reg_parser.add_argument('--phone', help='Phone number')
    reg_parser.add_argument('--notes', help='Notes')
    
    list_parser = subparsers.add_parser('list-members', help='List members')
    list_parser.add_argument('--tier', help='Filter by tier')
    list_parser.add_argument('--status', help='Filter by status')
    
    add_pts_parser = subparsers.add_parser('add-points', help='Add points to member')
    add_pts_parser.add_argument('--member-id', required=True, help='Member ID or email')
    add_pts_parser.add_argument('--points', required=True, help='Points to add')
    add_pts_parser.add_argument('--reason', help='Reason for points')
    add_pts_parser.add_argument('--order-id', help='Related order ID')
    
    redeem_parser = subparsers.add_parser('redeem', help='Redeem reward')
    redeem_parser.add_argument('--member-id', required=True, help='Member ID or email')
    redeem_parser.add_argument('--reward-id', required=True, help='Reward ID')
    
    details_parser = subparsers.add_parser('member-details', help='Show member details')
    details_parser.add_argument('--member-id', required=True, help='Member ID or email')
    
    # Reward commands
    list_reward_parser = subparsers.add_parser('list-rewards', help='List rewards')
    list_reward_parser.add_argument('--active-only', action='store_true', help='Show only active')
    
    add_reward_parser = subparsers.add_parser('add-reward', help='Add new reward')
    add_reward_parser.add_argument('--name', required=True, help='Reward name')
    add_reward_parser.add_argument('--description', help='Description')
    add_reward_parser.add_argument('--points-cost', required=True, help='Points cost')
    add_reward_parser.add_argument('--reward-type', help='Type (discount, product, service)')
    add_reward_parser.add_argument('--value', help='Monetary value')
    
    # Transaction commands
    trans_parser = subparsers.add_parser('transactions', help='Show transactions')
    trans_parser.add_argument('--member-id', help='Filter by member')
    trans_parser.add_argument('--type', choices=['earn', 'redemption'])
    trans_parser.add_argument('--days', help='Show last N days')
    
    # Stats command
    subparsers.add_parser('stats', help='Show program statistics')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Initialize data files
    init_data_files()
    
    # Route to command handler
    commands = {
        'dashboard': cmd_dashboard,
        'register': cmd_register_member,
        'list-members': cmd_list_members,
        'add-points': cmd_add_points,
        'redeem': cmd_redeem,
        'list-rewards': cmd_list_rewards,
        'add-reward': cmd_add_reward,
        'transactions': cmd_transactions,
        'member-details': cmd_member_details,
        'stats': cmd_stats
    }
    
    try:
        return commands[args.command](args)
    except Exception as e:
        logger.error(f"Command failed: {e}")
        print(f"❌ Error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
